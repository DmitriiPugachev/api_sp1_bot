### Description:
Telegram bot which checks Yandex.Prakticum API for a homework status and sends this status via Telegram to the user.
#### You can:
  * just relax, this bot will check homework status for your;
  * search for new memes in Telegram chats and do nothing, while bot sends you all the status updates;
  * find all the error messages in ```.log``` file, if something went wrong.
#### Techs:
  * certifi==2020.4.5.1
  * cffi==1.14.0
  * chardet==3.0.4
  * cryptography==2.9.2
  * decorator==4.4.2
  * future==0.18.2
  * idna==2.9
  * pycparser==2.20
  * PySocks==1.7.1
  * pytest==6.2.1 
  * python-dotenv==0.13.0 
  * python-telegram-bot==12.7
  * python-telegram-handler==2.2.1
  * requests==2.23.0
  * six==1.15.0
  * tornado==6.0.4
  * urllib3==1.25.9
### How to run the project local:
Clone the repo and go to its directory:
```bash
git clone https://github.com/DmitriiPugachev/api_sp1_bot
```
```bash
cd api_sp1_bot
```
Create and activate virtual environment:
```bash
python3 -m venv env
```
```bash
source env/bin/activate
```
Install and upgrade pip:
```bash
python3 -m pip install --upgrade pip
```
Install all the dependencies from a ```requirements.txt``` file:
```bash
pip install -r requirements.txt
```
Create a ```.env``` file in the root directory and fulfill it like ```.env.example```.

Run bot on your local machine:
```bash
python3 homework.py
```

### How to deploy the project on a remote server:
Fork [this repo](https://github.com/DmitriiPugachev/api_sp1_bot) to your
GitHub account.

F.e. you can use [Heroku](https://www.heroku.com/) or any other hosting service.

If you use Heroku, then register and create new application.

Next go to "Deploy" section and connect your GitHub account with your Heroku account.

Afterwards push "Deploy Branch" button.

Further, go to "Config Vars" in a "Settings" section and with a "Reveal Config Vars" button add all the environmental variables like in ```.env.example``` to Heroku.

To activate this bot go to "Resources" section and turn the worker switch on.  

### Author
Dmitrii Pugachev
