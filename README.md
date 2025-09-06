# Telegramm Miniapp Example

simple repo that may be used as start point for your project

## Stack

### Frontend

this template uses **VueJs** as base js framework, also here is a uilib and simple iconpack

- **Daisy UI**: css ui lib based on tailwindcss (use by classnames)
- **RemixIcons**: material-design like icons (use by classnames)
- **PocketBase JS SDK**: datastore and auth (use by client import)
- **TGMiniApps SDK**: integration with telegram (official js script)

### Backend

for simpler usage expireance this temlpate we choose **PocketBase** as **go** backend framework with data storage, auth(OTP, emails, Oauth 2FA)
Also this backend supports simple migrations and hooks on js or go!
**PocketBase** can also act as a **server** for static build files of **frontend** & **admin panel** with comfort editing tables ui

### TelegramBot

base **python** version of this project: **3.13**
lib for communicate with _TelegramApi_: **PyTelegramBotApi**

#### Libs

- **PyTelegramBotApi**: official async/sync lib for communicate with _TelegramApi_
- **python-decouple**: env use
- **rich**: colored console output and logs
- **pocketbase**: communicate with pocketbase instance

### Features

- Check that app openned as telegram miniapp
- Check hash of initData for sequrity authorisation
- PocketBase jshook for handle auth requests from telegram
- Docker based system for automatisation build process
- Support VueJs Router
- Base App Example with themes

## Requirements

### For Run

- installed **git**
- installed docker & docker-compose v2
- **.env** files (copy from .env.example with data in fields)
- one free port (change in ./pocketbase/dockerfile lines 18 & 21 same values) with support of **HTTPS** protocol

#### Run Prepare

all steps from dev prepare, excluding marked steps
finally run:

- for create containers and run it in background: `docker-compose up -d`

### For Develop

- **all run requirements**
- installed **python 3.13**
- two free ports (5173 fow web & 8090 for pocketbase) **with HTTPS/HTTP** protocol
- recomended: **VSCode** with extensions:
  - Vue (Official) & Tailwind CSS IntelliSense
  - Python & Pylance & Ruff (optional Python Environments)
  - Prettier
  - ContainerTool
- installed latest stable version **NodeJS** & **npm** (installs with nodeJS) or any NodeJS package manager (pmpm / yarn / etc)

#### Dev Prepare

0. register bot in BotFather and get api key
1. copy this repo `git clone https://github.com/sht0rmx/MiniAppTemplate` **(if you deploy your project, replace link to your app repo link)**
2. run VSCode and open `MiniAppTemplate` **(dont open VSC for pruduction deploy prepare)**
3. run console `Ctrl+J` in IDE window **(skip 1-3 steps for pruduction)**
   1. open `ports` tab and click **forward port** (ex: 5173 & 8090)
   2. change privacy of this ports to **public**
   3. remember link for this ports
   4. setup **miniapp button** and **miniapp** in BotFather with url of forwarded **5173** port (for production paste link to runed pocketbase instance base port 5432)
   - port forward need recreate with every restart of VSC instance **(dont worry url will be keepd ~within the 1st month)**
4. open pocketbase dir `cd pocketbase`
   1. download release for your system [PocketBase](https://github.com/pocketbase/pocketbase/releases/tag/v0.29.3)
   2. copy executable into **./pocketbase/** folder
   3. run binary file
      - win: `./pocketbase.exe serve`
      - linux: `./pocketbase serve`
   4. open link from console and register root account
   5. in admin panel open **env** collection and insert record `key: "BOT_TOKEN" value: "bot api key from 1 step"` and save collection
   - run command `nmp run dev` **(on dev stage)**
5. open frontend dir `cd frontend` **(skip 5th step for pruduction)**
   1. run `npm install` (or your NodeJS pkg manager install command)
   2. copy **.env.example** as **.env**
   3. paste forward 8090 port url to **VITE_POCKETBASE_URL**
   4. **TG_MINIAPP_START** insert the link for start bot miniapp in format `http://t.me/botusername/?startapp`
   5. run vite server with autoreload with `nmp run dev`
   - run command `nmp run dev` **(on dev stage)**
6. open bot directory `cd bot`
   1. create virtual enviroment by command:
      - win: `python -m venv .venv`
      - linux: `python3 -m venv .venv`
   2. activate venv:
      - win: `./.venv/Scripts/activate.bat` or in PowerShell `./.venv/Scripts/activate.ps1`
      - linux: `source ./.venv/bin/activate`
   3. install requirements `pip install -r requirements.txt`
   4. copy **.env.example** as **.env**
   5. paste api key in TOKEN field
   6. paste PB_URL & ADMIN_EMAIL & ADMIN_PASSWORD for right bot work with db
   - run command:
      - win: `python ./main.py`
      - linux: `python3 ./main.py`

## Thanks

created by @shtormx with help from @dima0409 in 2025y
