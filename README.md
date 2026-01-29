### Welcome to Aurora/Nemo!

A local AI assistant project built in Python using TTS, STT, and memory logging.

---

This project is currently under development of its second iteration on the `dev` branch. The `pi` branch has the deployable version on the Raspberry Pi.

The device is not currently HIPAA compliant. Requests are passed to an API using the Model `Meta LLaMA 3.2` (if this doesn't run, see backup: `Google Gemma 3.2b`). 

Please do not pass sensitive information to the device in its current state. Your information may not be kept private. Do not trust the AI on everything spoken. Hallucinations are still present as of the last test date of this project. 

Last test date: `January 2nd, 2026`

The wake-word engine will not work when ran from a computer. It is a downloaded wake-word engine from Picovoice via Porcupine: `Hey Nemo`

Please use a Raspberry Pi when running it.

# Suggested Hardware

For this project, I strongly suggest the following capable hardware:

-Headphones. If they record at 16000, excellent. If they record at 41000, use `resampy`. If they do not record at either, check requirements file once updated.

-Raspberry Pi 5. Run a model 5. Make sure you have a fan as well as a heat sink. The Pi heats up very quickly, especially when trying to run LLMs. Although the LLM isn't run locally, the next iteration is looking to run it locally via a Raspberry Pi AI HAT 2+. This is a future aspiration of this project.

-A keyboard to pass inputs. As of the first and second variations of this project, it does require the command `python nemo.py` to be run (DO NOT run `main.py`).

-A microphone for inputs. Ideally, your headphones can both record and hear. Again, this needs to be either 16000 or 41000. 

# System Requirements

-The second iteration of the repository ( updated `Jan 20th ` ) does not require a heavy system to run. Resources are cleared. 

# Deployment Instructions

-Some basic things if you've never done this sort of thing before:

1) Boot a new terminal in your Raspberry Pi.
2) run `git clone https://github.com/LynxAndIbex/nemo_aurora`
3) ensure python is installed (python3 --version) and pip is installed (pip --version). you might have some trouble on python 3.11. If you see an error about audio.kwargs (sounddevice error), force deprecate to Python 3.9. 
4) make sure to activate a virtual environment. this project has a LOT of libraries that you really don't want in your global instances. this can be done via `python -m venv venv` followed by `.venv/bin/activate`
5) install the requirements file, which has recently been updated in v2 `pip install -r requirements.txt`
6) now you should be good to run the project locally. 

# Notes on publication

This project is open source MIT licensed. Retextures and changes in modular flow most be documented and credit appropriately. 


README last updated on: `January 29, 2026`