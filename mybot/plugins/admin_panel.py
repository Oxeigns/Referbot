"""Admin panel callbacks and interactions."""

from __future__ import annotations

from bson import ObjectId
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from ..services.channels import verify_bot_channel_access
from ..ui import keyboards, messages
from ..utils import log_errors


async def show_admin_panel(client: Client, message: Message, locale: str) -> None:
    context = client.app_context
    text = messages.admin_panel_text(context.translator, locale=locale)
    keyboard = keyboards.admin_panel_keyboard(context.callback_signer)
    try:
        await message.edit_text(text, reply_markup=keyboard)
    except Exception:  # pragma: no cover - depends on chat state
        await message.reply_text(text, reply_markup=keyboard)


async def handle_admin_callback(client: Client, callback: CallbackQuery, payload) -> None:
    context = client.app_context
    action = payload.action
    locale = callback.from_user.language_code or context.config.locale
    service = client.admin_service

    if action == "admin:broadcast":
        keyboard = keyboards.admin_broadcast_keyboard(context.callback_signer)
        if callback.message:
            await callback.message.reply_text("Choose broadcast audience:", reply_markup=keyboard)
        await callback.answer()
        return

    if action == "admin:broadcast_all":
        context.admin_state.set(callback.from_user.id, {"type": "broadcast", "scope": "all"})
        await callback.answer("Send the broadcast message.", show_alert=True)
        return

    if action == "admin:broadcast_active":
        context.admin_state.set(callback.from_user.id, {"type": "broadcast", "scope": "active"})
        await callback.answer("Send the broadcast message.", show_alert=True)
        return

    if action == "admin:broadcast_filtered":
        context.admin_state.set(
            callback.from_user.id,
            {"type": "broadcast_filtered", "stage": "threshold"},
        )
        await callback.answer("Send the minimum points threshold.", show_alert=True)
        return

    if action == "admin:users":
        keyboard = keyboards.admin_users_keyboard(context.callback_signer)
        if callback.message:
            await callback.message.reply_text("User management:", reply_markup=keyboard)
        await callback.answer()
        return

    if action == "admin:users_search":
        context.admin_state.set(callback.from_user.id, {"type": "user_search"})
        await callback.answer("Send a user ID or username to search.", show_alert=True)
        return

    if action == "admin:users_ban":
        context.admin_state.set(callback.from_user.id, {"type": "user_ban", "banned": True})
        await callback.answer("Send the user ID to ban.", show_alert=True)
        return

    if action == "admin:users_unban":
        context.admin_state.set(callback.from_user.id, {"type": "user_ban", "banned": False})
        await callback.answer("Send the user ID to unban.", show_alert=True)
        return

    if action == "admin:users_points":
        context.admin_state.set(callback.from_user.id, {"type": "user_points"})
        await callback.answer("Send 'user_id delta'.", show_alert=True)
        return

    if action == "admin:users_export":
        buffer = await service.export_users_csv()
        if callback.message:
            await callback.message.reply_document(buffer, file_name="users.csv")
        await callback.answer("Export generated.")
        return

    if action == "admin:referrals":
        keyboard = keyboards.admin_referrals_keyboard(context.callback_signer)
        if callback.message:
            await callback.message.reply_text("Referral review:", reply_markup=keyboard)
        await callback.answer()
        return

    if action == "admin:referrals_pending":
        pending = await service.list_referrals("pending")
        if pending:
            text = "Pending referrals:\n" + "\n".join(
                f"Referrer {doc['referrer']} -> User {doc['user']}" for doc in pending
            )
        else:
            text = "No pending referrals."
        if callback.message:
            await callback.message.reply_text(text)
        await callback.answer()
        return

    if action == "admin:referrals_qualified":
        qualified = await service.list_referrals("qualified")
        if qualified:
            text = "Qualified referrals:\n" + "\n".join(
                f"Referrer {doc['referrer']} -> User {doc['user']}" for doc in qualified
            )
        else:
            text = "No qualified referrals."
        if callback.message:
            await callback.message.reply_text(text)
        await callback.answer()
        return

    if action == "admin:payouts":
        keyboard = keyboards.admin_payouts_keyboard(context.callback_signer)
        if callback.message:
            await callback.message.reply_text("Payout operations:", reply_markup=keyboard)
        await callback.answer()
        return

    if action == "admin:payouts_pending":
        pending = await service.list_withdrawals("requested")
        if pending:
            text = "Pending withdrawals:\n" + "\n".join(
                f"ID {doc['_id']} — User {doc['user']} — {doc['points']} pts {doc['method']}"
                for doc in pending
            )
        else:
            text = "No pending withdrawals."
        if callback.message:
            await callback.message.reply_text(text)
        await callback.answer()
        return

    if action in {"admin:payouts_approve", "admin:payouts_reject", "admin:payouts_paid"}:
        status = {
            "admin:payouts_approve": "approved",
            "admin:payouts_reject": "rejected",
            "admin:payouts_paid": "paid",
        }[action]
        context.admin_state.set(callback.from_user.id, {"type": "payout_status", "status": status})
        await callback.answer("Send the withdrawal ID to update.", show_alert=True)
        return

    if action == "admin:settings":
        keyboard = keyboards.admin_settings_keyboard(context.callback_signer)
        if callback.message:
            await callback.message.reply_text("Runtime settings:", reply_markup=keyboard)
        await callback.answer()
        return

    if action == "admin:settings_ref_points":
        context.admin_state.set(callback.from_user.id, {"type": "settings", "key": "ref_points"})
        await callback.answer("Send the new points per referral.", show_alert=True)
        return

    if action == "admin:settings_min_withdraw":
        context.admin_state.set(
            callback.from_user.id,
            {"type": "settings", "key": "min_withdraw"},
        )
        await callback.answer("Send the new minimum withdrawal points.", show_alert=True)
        return

    if action == "admin:settings_channels":
        context.admin_state.set(
            callback.from_user.id,
            {"type": "settings", "key": "channels"},
        )
        await callback.answer(
            "Send channels to add/remove. Use +@channel to add, -@channel to remove, or a comma separated list to replace.",
            show_alert=True,
        )
        if callback.message:
            current = "\n".join(context.config.channels_display()) or "(none)"
            await callback.message.reply_text(f"Current channels:\n{current}")
        return

    if action == "admin:settings_support":
        context.admin_state.set(
            callback.from_user.id,
            {"type": "settings", "key": "support"},
        )
        await callback.answer("Send the support URL or 'none' to disable.", show_alert=True)
        return

    if action == "admin:settings_banner":
        context.admin_state.set(
            callback.from_user.id,
            {"type": "settings", "key": "banner"},
        )
        await callback.answer("Send the new banner image URL.", show_alert=True)
        return

    if action == "admin:settings_owner_logs":
        context.config.owner_logs_enabled = not context.config.owner_logs_enabled
        await service.update_setting("owner_logs_enabled", context.config.owner_logs_enabled)
        key = "admin.owner_logs_on" if context.config.owner_logs_enabled else "admin.owner_logs_off"
        await callback.answer(context.translator.t(key, locale=locale), show_alert=True)
        return

    if action == "admin:settings_test_channels":
        failures = await verify_bot_channel_access(client, context.config.channels_display())
        if callback.message:
            if failures:
                joined = "\n".join(failures)
                await callback.message.reply_text(
                    f"⚠️ Bot is missing access in:\n{joined}\nAdd the bot as an admin with member access."
                )
            else:
                await callback.message.reply_text("✅ Bot can access all configured channels.")
        await callback.answer("Channel access check complete.")
        return

    await callback.answer("Unhandled admin action", show_alert=True)


@Client.on_message(filters.private, group=2)
@log_errors
async def admin_message_handler(client: Client, message: Message) -> None:
    context = client.app_context
    if message.from_user.id != context.config.owner_id:
        return
    if not message.text:
        return
    state = context.admin_state.pop(message.from_user.id)
    if not state:
        return
    service = client.admin_service
    locale = message.from_user.language_code or context.config.locale

    if state.get("type") == "broadcast":
        delivered = await service.broadcast(
            client,
            message.text,
            scope=state.get("scope", "all"),
        )
        await message.reply_text(
            messages.broadcast_report_text(context.translator, locale=locale, delivered=delivered)
        )
        return

    if state.get("type") == "broadcast_filtered":
        if state.get("stage") == "threshold":
            try:
                threshold = int(message.text)
            except ValueError:
                await message.reply_text("Enter a valid integer threshold.")
                context.admin_state.set(
                    message.from_user.id,
                    {"type": "broadcast_filtered", "stage": "threshold"},
                )
                return
            context.admin_state.set(
                message.from_user.id,
                {"type": "broadcast_filtered", "stage": "message", "threshold": threshold},
            )
            await message.reply_text("Now send the broadcast message.")
            return
        delivered = await service.broadcast(
            client,
            message.text,
            scope="filtered",
            min_points=int(state.get("threshold", 0)),
        )
        await message.reply_text(
            messages.broadcast_report_text(context.translator, locale=locale, delivered=delivered)
        )
        return

    if state.get("type") == "user_search":
        results = await client.user_service.search(message.text)
        text = "\n".join(
            f"ID {doc['_id']} — {doc.get('profile', {}).get('first_name')} ({doc.get('points', 0)} pts)"
            for doc in results
        ) or "No users found."
        await message.reply_text(text)
        return

    if state.get("type") == "user_ban":
        try:
            target = int(message.text)
        except ValueError:
            await message.reply_text("Enter a valid user ID.")
            return
        updated = await client.user_service.set_banned(target, state.get("banned", False))
        if not updated:
            await message.reply_text("User not found.")
            return
        status = "banned" if state.get("banned") else "unbanned"
        await message.reply_text(f"User {target} {status}.")
        return

    if state.get("type") == "user_points":
        parts = message.text.split()
        if len(parts) != 2:
            await message.reply_text("Send 'user_id delta'.")
            return
        try:
            target = int(parts[0])
            delta = int(parts[1])
        except ValueError:
            await message.reply_text("Invalid numbers.")
            return
        updated = await service.adjust_points(target, delta=delta)
        if not updated:
            await message.reply_text("User not found.")
            return
        await message.reply_text(f"User {target} now has {updated['points']} points.")
        return

    if state.get("type") == "payout_status":
        try:
            withdrawal_id = ObjectId(message.text.strip())
        except Exception:
            await message.reply_text("Provide a valid withdrawal ID.")
            return
        updated = await client.withdrawal_service.set_status(
            withdrawal_id,
            status=state.get("status", "approved"),
            acted_by=message.from_user.id,
        )
        if not updated:
            await message.reply_text("Withdrawal not found.")
            return
        await message.reply_text(f"Withdrawal {updated['_id']} marked as {updated['status']}.")
        return

    if state.get("type") == "settings":
        key = state.get("key")
        if key == "ref_points":
            try:
                value = int(message.text)
            except ValueError:
                await message.reply_text("Enter an integer value.")
                return
            context.config.ref_points_per_ref = value
            await service.update_setting("ref_points_per_ref", value)
        elif key == "min_withdraw":
            try:
                value = int(message.text)
            except ValueError:
                await message.reply_text("Enter an integer value.")
                return
            context.config.min_withdraw_points = value
            await service.update_setting("min_withdraw_points", value)
        elif key == "channels":
            raw_parts = [
                part.strip()
                for part in message.text.replace("\n", ",").split(",")
                if part.strip()
            ]
            channels = list(context.config.required_channels)
            if any(part.startswith(('+', '-')) for part in raw_parts):
                for part in raw_parts:
                    op, value = part[0], part[1:].strip()
                    if not value:
                        continue
                    if not value.startswith("@") and not value.startswith("https://t.me/"):
                        await message.reply_text("Channels must start with @username or https://t.me/ URL.")
                        return
                    if op == '+' and value not in channels:
                        channels.append(value)
                    elif op == '-' and value in channels:
                        channels.remove(value)
            else:
                for part in raw_parts:
                    if not part.startswith("@") and not part.startswith("https://t.me/"):
                        await message.reply_text("Channels must start with @username or https://t.me/ URL.")
                        return
                channels = raw_parts
            context.config.required_channels = channels
            await service.update_setting("required_channels", channels)
        elif key == "support":
            value = message.text.strip()
            if value.lower() in {"none", "null", "off"}:
                context.config.support_url = None
                await service.update_setting("support_url", None)
            else:
                if not value.startswith("http"):
                    await message.reply_text("Provide a valid URL starting with http or https.")
                    return
                context.config.support_url = value
                await service.update_setting("support_url", value)
        elif key == "banner":
            value = message.text.strip()
            if not value:
                await message.reply_text("Provide a non-empty URL.")
                return
            context.config.banner_url = value
            await service.update_setting("banner_url", value)
        await message.reply_text(messages.settings_updated_text(context.translator, locale=locale))
        return
