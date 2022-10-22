# text2img
This is text-to-image Telegram bot

## How to install

### Preparing

#### Stable Diffusion API

You must create account in https://beta.dreamstudio.ai and generate API key

#### Telegram bot

You must create Telegram bot for this application

### Installation

#### Install with docker

1. `git clone https://github.com/the-sashko/text2img.git text2img`
2. `cd text2img`
3. `./scripts/deploy.sh`
4. Set up your data in `config/telegram.json` and `config/stable_diffusion.json` files

#### Install without docker
1. Install Python (version 3.10+)
2. Install Pip3
3. Install Virtualenv
4. `git clone https://github.com/the-sashko/text2img.git text2img`
5. `cd text2img`
6. `./scripts/install.sh`
7. Set up your data in `config/telegram.json` and `config/stable_diffusion.json` files

## How to use

### Run application

#### Run with docker container

1. `cd <PATH_TO_APPLICATION>`
2. `docker-compose up --detach`

#### Run without docker

1. `cd <PATH_TO_APPLICATION>`
2. `./scripts/run.sh`

### Send prompt to Telegram bot

#### You can improve prompt by using modificator on start of it
- `!` - improve prompt automaticaly
- `$` - add default image-to-image modifications
- For example `!$Test`

#### You can use image-to-image modification

- You can use image-to-image modification by adding them to end of prompt after `/`
- Format of image-to-image modification: `<prompt>:<strength>:<count_of_iterations>`
- `strength` is float number from 0.01 to 0.99
- `count_of_iterations` is int number from 5 to 150
- For example `Foo Bar/Yellow:0.5:30/Blue:0.5:30`
