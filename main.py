import nest_asyncio
nest_asyncio.apply()

import asyncio
import requests
from telegram import Bot
from telegram.ext import Application, JobQueue

# === CONFIGURAÇÕES ===
api_key = 'c5496cc3924912e21297274f9243f173'
token = '8302361033:AAG7RSVjyeARUPbnqqXowgeaC0j9aPNz_M8'
chat_id = '5305661461'

bot = Bot(token=token)

def buscar_time_id(nome_time):
    url = f'https://v3.football.api-sports.io/teams?search={nome_time}'
    headers = {'x-apisports-key': api_key}
    r = requests.get(url, headers=headers).json()
    return r['response'][0]['team']['id']

def buscar_jogo_ao_vivo(id_casa, id_fora):
    url = f'https://v3.football.api-sports.io/fixtures?live=all&team={id_casa}'
    headers = {'x-apisports-key': api_key}
    r = requests.get(url, headers=headers).json()
    jogos = r['response']
    for jogo in jogos:
        home = jogo['teams']['home']['id']
        away = jogo['teams']['away']['id']
        if (home == id_casa and away == id_fora) or (home == id_fora and away == id_casa):
            return jogo
    return None

def buscar_estatisticas(fixture_id):
    url = f'https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}'
    headers = {'x-apisports-key': api_key}
    r = requests.get(url, headers=headers).json()
    return r['response']

def buscar_eventos(fixture_id):
    url = f'https://v3.football.api-sports.io/fixtures/events?fixture={fixture_id}'
    headers = {'x-apisports-key': api_key}
    r = requests.get(url, headers=headers).json()
    return r['response']

# === Monitoramento contínuo ===
async def monitorar(context):
    id_casa = buscar_time_id('Botafogo')
    id_fora = buscar_time_id('Corinthians')
    jogo = buscar_jogo_ao_vivo(id_casa, id_fora)

    if jogo:
        fixture_id = jogo['fixture']['id']
        tempo = jogo['fixture']['status']['elapsed']
        gols = jogo['goals']
        estatisticas = buscar_estatisticas(fixture_id)
        eventos = buscar_eventos(fixture_id)

        msg = f"⏱️ {tempo} min - Botafogo x Corinthians\n"
        msg += f"🔢 Placar: {gols['home']} x {gols['away']}\n"

        for estat in estatisticas:
            if estat['team']['name'] in ['Botafogo', 'Corinthians']:
                for s in estat['statistics']:
                    if s['type'] == 'Corner Kicks':
                        msg += f"🚩 Escanteios {estat['team']['name']}: {s['value']}\n"

        await context.bot.send_message(chat_id=chat_id, text=msg)
    else:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Jogo ainda não começou ou não está ao vivo.")

# === Inicialização no Render ===
async def main():
    application = Application.builder().token(token).build()
    job_queue: JobQueue = application.job_queue

    job_queue.run_repeating(monitorar, interval=60, first=5)

    print("🤖 Bot está online e monitorando o jogo.")
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
