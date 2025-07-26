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
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data['response'][0]['team']['id']
    except Exception as e:
        print(f"[ERRO buscar_time_id] {e}")
        return None

def buscar_jogo_ao_vivo(id_casa, id_fora):
    url = f'https://v3.football.api-sports.io/fixtures?live=all&team={id_casa}'
    headers = {'x-apisports-key': api_key}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        jogos = r.json()['response']
        for jogo in jogos:
            home = jogo['teams']['home']['id']
            away = jogo['teams']['away']['id']
            if (home == id_casa and away == id_fora) or (home == id_fora and away == id_casa):
                return jogo
    except Exception as e:
        print(f"[ERRO buscar_jogo_ao_vivo] {e}")
    return None

def buscar_estatisticas(fixture_id):
    url = f'https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}'
    headers = {'x-apisports-key': api_key}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return r.json()['response']
    except Exception as e:
        print(f"[ERRO buscar_estatisticas] {e}")
        return []

def buscar_eventos(fixture_id):
    url = f'https://v3.football.api-sports.io/fixtures/events?fixture={fixture_id}'
    headers = {'x-apisports-key': api_key}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return r.json()['response']
    except Exception as e:
        print(f"[ERRO buscar_eventos] {e}")
        return []

async def monitorar(context):
    id_casa = buscar_time_id('Botafogo')
    id_fora = buscar_time_id('Corinthians')

    if not id_casa or not id_fora:
        await context.bot.send_message(chat_id=chat_id, text="❌ Não foi possível buscar os times.")
        return

    jogo = buscar_jogo_ao_vivo(id_casa, id_fora)

    if jogo:
        fixture_id = jogo['fixture']['id']
        tempo = jogo['fixture']['status']['elapsed']
        gols = jogo['goals']
        estatisticas = buscar_estatisticas(fixture_id)

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

async def main():
    application = Application.builder().token(token).build()
    job_queue: JobQueue = application.job_queue
    job_queue.run_repeating(monitorar, interval=60, first=5)
    print("🤖 Bot está online e monitorando o jogo.")
    await application.run_polling()

if _name_ == '_main_':
    asyncio.run(main())
