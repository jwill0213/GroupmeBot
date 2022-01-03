import gspread
import json
import os
import logging
from pytz import timezone, utc
from datetime import datetime
from time import sleep

from gspread.utils import ValueInputOption
from gspread_formatting import *

from Utils.redisUtils import getRedisClient
from Utils.cryptoUtils import findATH, getPriceDataForWatchlist
from Utils.groupmeUtils import send_message

DEBUG_LEVEL = logging.DEBUG if os.getenv("BOT_DEBUG") == "True" else logging.WARNING


def customTime(*args):
    utc_dt = utc.localize(datetime.utcnow())
    my_tz = timezone("US/Central")
    converted = utc_dt.astimezone(my_tz)
    return converted.timetuple()


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=DEBUG_LEVEL,
)

logging.Formatter.converter = customTime

SERVICE_ACCOUNT_DICT = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT"))

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = os.getenv("TEMPLATE_SPREADSHEET_ID")

PRICE_FORMAT = CellFormat(
    numberFormat=NumberFormat(type="CURRENCY", pattern="$#,##0.00######")
)

PERCENT_FORMAT = CellFormat(numberFormat=NumberFormat(type="PERCENT", pattern="0.000%"))

GREEN_COLOR_FORMAT = CellFormat(
    backgroundColor=Color(red=0.7176471, green=0.88235295, blue=0.8039216),
    backgroundColorStyle=ColorStyle(
        rgbColor=Color(red=0.7176471, green=0.88235295, blue=0.8039216)
    ),
)

GREATER_THAN_RULE = BooleanRule(
    condition=BooleanCondition("NUMBER_GREATER_THAN_EQ", ["0"]),
    format=GREEN_COLOR_FORMAT,
)

RED_COLOR_FORMAT = CellFormat(
    backgroundColor=Color(red=0.95686275, green=0.78039217, blue=0.7647059),
    backgroundColorStyle=ColorStyle(
        rgbColor=Color(red=0.95686275, green=0.78039217, blue=0.7647059)
    ),
)

LESS_THAN_RULE = BooleanRule(
    condition=BooleanCondition("NUMBER_LESS", ["0"]), format=RED_COLOR_FORMAT
)


def main():
    gc = gspread.service_account_from_dict(SERVICE_ACCOUNT_DICT)
    r = getRedisClient()

    # Each kep represents 1 bot hash
    bots = [k for k in r.keys() if len(k) == 26]
    for botID in bots:
        # find the existing spreadsheet if it exists. Otherwise create a new one
        if r.hexists(botID, "watchlist"):
            if r.hexists(botID, "spreadsheet"):
                spreadsheet = gc.open_by_url(r.hget(botID, "spreadsheet"))
            else:
                spreadsheet = gc.copy(
                    SAMPLE_SPREADSHEET_ID, f"Crypto Data", copy_permissions=True
                )
                spreadsheet.share("", perm_type="anyone", role="reader")
                r.hset(botID, "spreadsheet", spreadsheet.url)

        # Get watchlist data for the bot
        priceData = getPriceDataForWatchlist(botID)

        # Loop through all symbols in the watchlist and create a worksheet for each one.
        for symbol, quote in priceData["quotes"].items():
            # Before each sheet update, we want to sleep for 15 seconds to avoid tripping the google sheets api limit
            logging.info("Sleeping for 15 seconds to avoid google sheets api limit")
            sleep(15)
            logging.info(f"Finished sleeping, processing {symbol} for bot {botID}")
            dataDatetime = priceData["dataDate"]
            if symbol in [w.title for w in spreadsheet.worksheets()]:
                sheet = spreadsheet.worksheet(symbol)
            else:
                template = spreadsheet.worksheet("Template")
                sheet = spreadsheet.duplicate_sheet(
                    source_sheet_id=template.id,
                    new_sheet_name=symbol,
                    insert_sheet_index=0,
                )

            startCell = sheet.find("Datetime")

            # Record price
            sheetUpdate = sheet.append_row(
                [dataDatetime, quote["currentPrice"]],
                value_input_option=ValueInputOption.user_entered,
                table_range=startCell.address,
            )

            # Find the cells to update with percent change
            dateCell, priceCell = (
                sheetUpdate["updates"]["updatedRange"].split("!")[1].split(":")
            )

            cellFormatList = [(priceCell, PRICE_FORMAT)]

            updatedRow = int(dateCell[1:])
            if updatedRow > 2:
                priceChangeCell = sheet.find("Price Change").address[0] + str(
                    updatedRow
                )
                percentChangeCell = sheet.find("Percent Change").address[0] + str(
                    updatedRow
                )
                lastPriceCell = f"{priceCell[0]}{int(priceCell[1:]) - 1}"

                priceChangeFormula = f"={lastPriceCell}-{priceCell}"
                percentChangeFormula = f"={priceChangeCell}/{lastPriceCell}"

                sheet.update_acell(priceChangeCell, priceChangeFormula)
                sheet.update_acell(percentChangeCell, percentChangeFormula)

                cellFormatList.append((priceChangeCell, PRICE_FORMAT))
                cellFormatList.append((percentChangeCell, PERCENT_FORMAT))

                formattingRange = GridRange.from_a1_range(
                    f"{priceChangeCell}:{percentChangeCell}", sheet
                )

                formattingRules = [
                    ConditionalFormatRule(
                        ranges=[formattingRange], booleanRule=GREATER_THAN_RULE
                    )
                ]
                formattingRules.append(
                    ConditionalFormatRule(
                        ranges=[formattingRange], booleanRule=LESS_THAN_RULE
                    )
                )

                rules = get_conditional_format_rules(sheet)
                rules.extend(formattingRules)
                rules.save()

            # Check for All Time High update
            athHeaderCell = sheet.find("All Time High")
            cellAddress = athHeaderCell.address[0] + str(
                int(athHeaderCell.address[1:]) + 1
            )
            athCell = sheet.acell(cellAddress)
            athData = findATH(quote["slug"])
            logging.debug(f"All Time High data found {athData}")
            if athData:
                newATH = float(athData[0].replace("$", "").replace(",", ""))
                if athCell.value:
                    existingATH = float(athCell.value.replace("$", "").replace(",", ""))
                    if newATH > existingATH:
                        # New All Time high
                        logging.debug(
                            f"New All Time High\nOld:{existingATH}  New:{newATH}"
                        )
                        sheet.update_acell(cellAddress, newATH)
                        send_message(
                            f"New All Time High for {symbol} of {newATH}!", botID
                        )
                else:
                    # No existing all time high data, so set it.
                    logging.debug(f"No All Time High data found. Updating to {newATH}")
                    sheet.update_acell(cellAddress, newATH)
                    cellFormatList.append((cellAddress, PRICE_FORMAT))

            # Batch update all cells
            logging.debug(f"FORMAT LIST: {cellFormatList}")
            batch_updater(spreadsheet).format_cell_ranges(
                sheet, cellFormatList
            ).execute()


if __name__ == "__main__":
    main()
