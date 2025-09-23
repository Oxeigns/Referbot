"""Inline callback handlers."""

from __future__ import annotations

from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.types import CallbackQuery, Message

from ..services.channels import ensure_membership
from ..ui import keyboards, messages
from ..utils import RateLimitExceeded, log_errors, notify_owner


async def _render_home(client: Client, message: Message, locale: str) -> None:
    context = client.app_context
    user_doc = await client.user_service.get(message.chat.id)
    text = messages.home_text(
        context.translator,
        locale=locale,
        user=user_doc,
        config=context.config,
        referral_link=context.referral_link(message.chat.id),
    )
    keyboard = keyboards.home_keyboard(
        context.callback_signer,
        config=context.config,
        is_owner=message.chat.id == context.config.owner_id,
    )
    if message.photo:
        await message.edit_caption(
            text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.edit_text(
            text,
            reply_markup=keyboard,
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML,
        )


@Client.on_callback_query()
@log_errors
async def callbacks_handler(client: Client, callback: CallbackQuery) -> None:
    context = client.app_context
    user = callback.from_user
    if not user:
        return
    locale = user.language_code or context.config.locale
    try:
        payload = context.callback_signer.unpack(callback.data or "")
    except ValueError:
        await callback.answer("Invalid action", show_alert=True)
        return
    action = payload.action

    if action == "home":
        if callback.message:
            await _render_home(client, callback.message, locale)
        await callback.answer()
        return

    if action == "channels":
        keyboard = keyboards.channels_keyboard(
            context.callback_signer, context.config.channels_display()
        )
        await callback.answer()
        if callback.message:
            await callback.message.reply_text(
                messages.channels_overview_text(
                    context.translator,
                    locale=locale,
                    channels=context.config.channels_display(),
                ),
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )
        return

    if action == "noop":
        await callback.answer()
        return

    if action == "verify":
        try:
            context.verify_rate_limiter.hit("verify", user.id)
        except RateLimitExceeded:
            await callback.answer("Please wait before verifying again.", show_alert=True)
            return
        if not context.config.required_channels:
            await callback.answer("No channels configured.", show_alert=True)
            return
        is_member, missing = await ensure_membership(
            client,
            user.id,
            context.config.required_channels,
            cache=context.channel_access_cache,
        )
        if not is_member:
            failure_text = messages.verify_failure_text(
                context.translator,
                locale=locale,
                channels=context.config.required_channels,
                missing=missing,
            )
            if callback.message:
                await callback.message.reply_text(failure_text, disable_web_page_preview=True)
            await callback.answer("Join all required channels and try again.", show_alert=True)
            return
        referral = await client.referral_service.qualify(user.id)
        if referral and referral.get("referrer"):
            await client.user_service.add_points(referral["referrer"], context.config.ref_points_per_ref)
            notify = (
                f"🎉 Your referral {user.first_name or user.id} just qualified! +{context.config.ref_points_per_ref} points."
            )
            await client.send_message(referral["referrer"], notify)
            await notify_owner(
                client,
                (
                    "✅ Referral qualified\n"
                    f"Referrer: {referral['referrer']}\nUser: {user.id}"
                ),
            )
        success_text = messages.verify_success_text(
            context.translator, locale=locale, ref_points=context.config.ref_points_per_ref
        )
        if callback.message:
            await callback.message.reply_text(success_text)
        await callback.answer("Verification complete!", show_alert=True)
        return

    if action == "link":
        link = context.referral_link(user.id)
        if not link:
            await callback.answer("Referral link unavailable", show_alert=True)
            return
        await callback.answer()
        if callback.message:
            await callback.message.reply_text(
                messages.referral_link_text(context.translator, locale=locale, link=link)
            )
        return

    if action == "points":
        user_doc = await client.user_service.get(user.id)
        stats = await client.referral_service.stats(user.id)
        text = messages.points_text(
            context.translator, locale=locale, points=user_doc.get("points", 0), stats=stats
        )
        await callback.answer()
        if callback.message:
            await callback.message.reply_text(text, parse_mode=ParseMode.HTML)
        return

    if action == "leaderboard":
        top = await client.user_service.top_users(limit=10)
        text = messages.leaderboard_text(context.translator, locale=locale, entries=top)
        await callback.answer()
        if callback.message:
            await callback.message.reply_text(text)
        return

    if action == "support":
        await callback.answer("Contact support", show_alert=True)
        return

    if action == "admin":
        if user.id != context.config.owner_id:
            await callback.answer("Admins only", show_alert=True)
            return
        from .admin_panel import show_admin_panel

        if callback.message:
            await show_admin_panel(client, callback.message, locale)
        await callback.answer()
        return

    if action == "withdraw":
        doc = await client.user_service.get(user.id)
        if doc.get("points", 0) < context.config.min_withdraw_points:
            await callback.answer(
                f"You need at least {context.config.min_withdraw_points} points to withdraw.",
                show_alert=True,
            )
            return
        context.pending_withdrawals[user.id] = {"stage": "method", "points": doc.get("points", 0)}
        keyboard = keyboards.withdraw_method_keyboard(context.callback_signer)
        await callback.answer()
        if callback.message:
            await callback.message.reply_text(
                messages.withdraw_prompt_text(
                    context.translator, locale=locale, minimum=context.config.min_withdraw_points
                ),
                reply_markup=keyboard,
            )
        return

    if action == "withdraw_method":
        pending = context.pending_withdrawals.get(user.id)
        if not pending:
            await callback.answer("No pending withdrawal.", show_alert=True)
            return
        method = payload.data.get("method", "")
        pending.update({"method": method, "stage": "awaiting_address"})
        await callback.answer("Send your payout address.", show_alert=True)
        return

    if action == "help":
        text = messages.help_text(context.translator, locale=locale, config=context.config)
        await callback.answer()
        if callback.message:
            await callback.message.reply_text(
                text,
                disable_web_page_preview=True,
                parse_mode=ParseMode.HTML,
            )
        return

    if action.startswith("admin"):
        from .admin_panel import handle_admin_callback

        await handle_admin_callback(client, callback, payload)
        return

    await callback.answer("Unhandled action", show_alert=True)
