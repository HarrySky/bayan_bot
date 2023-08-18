# Telegram Bayan Bot

Telegram group chat bot that detects similar memes (images)

## Roadmap

- [ ] WebHooks instead of polling
- [ ] all chat images importing
- [ ] statistics

## Deployment

How to deploy your own Bayan Bot

1. Create bot (see https://core.telegram.org/bots/tutorial)
2. Add bot to group chat
3. Give bot admin rights (**otherwise it would not see all messages**)
4. Get chat ID
    1. Write something to chat
    2. Go to `https://api.telegram.org/bot{BOT_TOKEN}/getUpdates` with token `BotFather` gave you
    3. Find chat ID in JSON response you received
5. Move this repo to your server
    1. Docker and Docker Compose v2 MUST be installed
6. Run `./scripts/build_bot_image` script (uses `sudo`)
7. Create `/opt/CHAT_NAME` folder on server
8. Replace variables and paths in `.cd/docker-compose.yml`
    1. `BOT_TOKEN` value should be the token `BotFather` gave you
    2. `GROUP_CHAT_ID` value should be the ID of the chat bot should monitor
    3. replace `CHAT_NAME` placeholder in `DATABASE_URL`
    4. replace `CHAT_NAME` placeholder in volumes to folder you created in step 7
9. Run `./scripts/deploy_bot` script (uses `sudo`)
10. Check logs via `docker logs -t -f bayan_bot`
