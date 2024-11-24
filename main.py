from init import client, token, log, routes, app, web, PORT
from server import handlers
import asyncio
import events.on_interaction
import events.on_ready
import events.on_message

async def main():
    log.info("Démarrage du serveur...")
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    log.info(f'Serveur interne en ligne sur localhost:{PORT}')
    log.info("Connexion à Discord...")
    await client.login(token)
    log.info("Connecté")
    await client.connect()

async def clear():
    events.on_ready.stop_tasks()
    await client.close()
    client.clear()
    log.debug("Déconnecté  ")

if __name__ == '__main__':
    log.info("Création de la boucle asyncio...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    
    except KeyboardInterrupt:
        loop.run_until_complete(clear())