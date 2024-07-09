import json
import asyncio
from settings import BOT_BASE_DIR

WARNINGS_FILE = f'{BOT_BASE_DIR}/json/warnings.json'


async def load_warnings():
    with open(WARNINGS_FILE, 'r', encoding='utf-8') as file:
        return json.load(file)


async def save_warnings(warnings):
    with open(WARNINGS_FILE, 'w', encoding='utf-8') as file:
        json.dump(warnings, file, ensure_ascii=False, indent=4)


async def main():
    warnings = {
        "user1": [
            {"warn_number": 1, "date": "2024-04-02"},
            {"warn_number": 2, "date": "2024-04-03"},
            {"warn_number": 3, "date": "2024-04-04"}
        ],
        "user2": [
            {"warn_number": 1, "date": "2024-04-01"},
            {"warn_number": 2, "date": "2024-04-02"}
        ]
    }
    await save_warnings(warnings)
    load = await load_warnings()
    print(load)

asyncio.run(main())

