#!/usr/bin/python3

import discord
import random
import datetime
import requests
import json
from datetime import timezone

client = discord.Client()

supportbot_id = "<@415988497233477637>"
supportbot_user = "SupportBot#7329"

smartrewards_id = "<@406978568145338381>"
tipbot_id = "<@384266669016743936>"
andrew_id = "<@383504587489017856>"

main_tipping_channel = "389238821788712961"


def log_interaction(message):
    print("User: " + str(message.author) + " ({0.author.mention})\nChannel: ".format(message) + str(message.channel) + "\nTrigger: " + str(message.content) + "\n",flush=True)


@client.event
async def on_message(message):
    # Ignore our own messages
    if supportbot_user in str(message.author):
        pass


    # Somone mentions support_bot or sends a DM
    elif supportbot_id in message.content or 'Direct' in str(message.channel):


        # Tipbot replies to someone tipping me, confirming it happened
        if tipbot_id in message.author.mention:
            log_interaction(message)
            tipper = message.content.split(", ")[0]
            if message.channel != main_tipping_channel:
                await client.send_message(message.channel, "That's very generous of you " + tipper + ", but I'm afraid I can't accept that! I'll take care of this in <#".format(message) + main_tipping_channel + ">")
            else:
                await client.send_message(message.channel, "That's very generous of you " + tipper + ", but I'm afraid I can't accept that!")
            amount = message.content.split("Tipped " + supportbot_id + " Σ")[1].split(" SMART")[0]
            client.send_message(client.get_channel(main_tipping_channel),tipbot_id + " tip " + squadrewards_id + " %s" %amount)


        # Abuse
        elif "you suck" in message.content.lower() or "you're stupid" in message.content.lower() or "go die" in message.content.lower() or "fuck you" in message.content.lower() or "an idiot" in message.content.lower() or "you're dumb" in message.content.lower():
            log_interaction(message)
            await client.send_message(message.channel, "Bots have feelings too {0.author.mention}. You'll have to take this up with my handler ".format(message) + andrew_id)


        # DEBUG.LOG
        elif "clear" in message.content.lower() and "log" in message.content.lower():
            log_interaction(message)
            await client.send_message(message.channel, '''Here's what I know about clearing debug.log: The debug.log file quickly gets very large. You must periodically clear the file's contents. You can do that by restarting `smartcashd` or with the following linux command: `truncate --size 0 ~/.smartcash/debug.log` (if you are not currently logged in as the user running smartcashd, you will need to switch to them first).

Check out "Setup cronjob to clear debug.log" on http://smartnodes.cc/#SmartNode_Hardening for more details, and make sure you configure the Discord bot to monitor your SmartNode and alert you of any problems: https://steemit.com/smartcash/@dustinface/smartnodemonitorbot''') 


        # SMARTNODE PAYOUT 
        elif "smartnode" in message.content.lower() and "payout" in message.content.lower():
            log_interaction(message)
            await client.send_message(message.channel, '''SmartNodes that are `Enabled` should be paid every 7-12 days. See https://cdn.discordapp.com/attachments/391232540133818368/411786869538553856/SmartNode_Payment_Determination_R3.pdf for further info on how the payment cycle works.

You can estimate your SmartNode income by using https://smartcash.bitcoiner.me/smartnodes/calculator/. Also see http://smartnodes.cc/ for more information.''')


        # Check address for SmartRewards eligibility
        elif "smartrewards check " in message.content.lower() or "check smartrewards " in message.content.lower():
            log_interaction(message)
            valid = False
            success = True
            reason = ""
            await client.send_message(message.channel, "Give me a minute to look that up " + message.author.mention)
            address = message.content.split(" ")[-1]

            while True:
                try:
                    balance,transactions = get_address(address)
                    if balance < 1000:
                        valid = False
                        reason = "it holds less than 1,000 SMART"
                        break
                    if walk_backwards(address,balance,transactions) > 1000:
                        outgoing_times = get_outgoing_timestamps(transactions)
                        valid,reason,payout = check_validity(balance,outgoing_times)
                        break
                    else:
                        valid = False
                        reason = "it had a balance below 1000 when the snapshot was taken."
                        break

                except KeyError:
                    await client.send_message(message.channel, "Sorry " + message.author.mention + " I couldn't find that address on the explorer.")
                    success = False
                    break

                except:
                    await client.send_message(message.channel, "Sorry " + message.author.mention + " I had a problem getting that information.")
                    success = False
                    break


            if success:
                if valid == True:
                    await client.send_message(message.channel, message.author.mention + ", the address " + address + " is **eligible** for SmartRewards this month which will be paid on " + payout + ".. (results of this beta feature may be unexpected)")
                else:
                    await client.send_message(message.channel, message.author.mention + ", the address " + address + " is **ineligible** for SmartRewards this month because " + reason + ". (results of this beta feature may be unexpected)")


        # SMARTREWARDS
        elif "smartrewards" in message.content.lower():
            log_interaction(message)
            await client.send_message(message.channel, '''Snapshots are taken on the 25th of each month. You will earn SmartRewards on **any** address for which you hold the keys (web or desktop, SmartNode included!) which holds >=1000 SMART for one month and does not make **any** outgoing transactions during that time. Please note, most exchanges do _not_ pay SmartRewards to their users, holding >= SMART in an exchange does not gurantee a reward. Check with your exchange's support for details.

See https://smartcash.cc/what-are-smartrewards/#toggle-id-6 https://smartcash.bitcoiner.me/ and http://smartrewards.ccodam.dk/ for more details.''')


        # SMARTHIVE VOTING
        elif "smarthive" in message.content.lower():
            log_interaction(message)
            await client.send_message(message.channel, "SmartCash holders get a say in what project are funded from our community hive budget. These projects help further SmartCash in many different ways. You can view and vote on SmartHive Proposals at https://vote.smartcash.cc/. More information on **how** to vote can be found at https://forum.smartcash.cc/t/how-to-vote-on-a-smartcash-proposal/388")


        # EXPIRED NEW START #
        elif "expired" in message.content.lower() or "start" in message.content.lower() or "missing" in message.content.lower():
            log_interaction(message)
            await client.send_message(message.channel, "Sometimes SmartNodes need to be restarted for various reasons. Check out https://steemit.com/smartnodes/@apt99/help-my-smartnode-is-missing-or-expired-or-a-new-start-is-required for more information")
 

        # Upgrade
        elif "upgrade" in message.content.lower() or "update" in message.content.lower():
            log_interaction(message)
            await client.send_message(message.channel, '''Updating your SmartNode to the latest release is a multi-step process: 
1) Stop smartcashd on your SmartNode, delete peers.dat, update the wallet, and then start smartcashd
2) Upgrade your desktop or "hot" wallet to the latest version
3) After upgrading you SmartNode you will need to issue a new start from your desktop wallet by highlighting your node and clicking `start-alias` (Warning: This will reset your SmartNode's position in the payment queue)

**Note: When you start `smartcashd` on your updated node its status will be `Not capable smartnode: Invalid protocol version` until you complete step 3.**

For more information see http://smartnodes.cc/#Mandatory_Upgrade_v1.1.1''')

        
        # INSTALL
        elif "install.sh" in message.content.lower():
            log_interaction(message)
            await client.send_message(message.channel, "https://github.com/SmartCash/smartnode. Also see http://smartnodes.cc/ for more information and make sure you can configure the Discord bot to monitor you SmartNode and alert you of any problems https://steemit.com/smartcash/@dustinface/smartnodemonitorbot")


        # SMARTNODE MONITOR
        elif "monitor" in message.content.lower():
            log_interaction(message)
            await client.send_message(message.channel, "You can use the Discord bot to monitor you SmartNode and alert you of any problems https://steemit.com/smartcash/@dustinface/smartnodemonitorbot")


        # GUIDE
        elif "guide" in message.content.lower():
            log_interaction(message)
            await client.send_message(message.channel, "http://smartnodes.cc/#SmartNode_Setup")


        # BOOTSTRAP
        elif "bootstrap" in message.content.lower():
            log_interaction(message)
            await client.send_message(message.channel, '''txindex=1 version: https://proteanx.com/txindexstrap.zip
non-txindex=1 version: https://proteanx.com/bootstrap.zip

Instructions can be found at https://smartcash.freshdesk.com/support/solutions/articles/35000027174-using-the-bootstrap-to-speedup-sync-when-upgrade-wallet. Also see http://smartnodes.cc/#SmartNode_FAQ for more information.''')


        # TROUBLESHOOT
        elif "troubleshoot" in message.content.lower():
            log_interaction(message)
            await client.send_message(message.channel, "Check out this guide for general SmartNode troubleshooting procedures: https://smartcash.blockchainlibrary.org/2018/02/troubleshooting-guidance-for-your-smartcash-smartnode-vps/")


        # SMARTNODE CHART
        elif "chart" in message.content.lower():
            log_interaction(message)
            await client.send_message(message.channel, "https://smartnode.aneis.ch/smartnode_chart.html")


        # SMARTNODE CALCULATOR
        elif "calculator" in message.content.lower():
            log_interaction(message)
            await client.send_message(message.channel, "https://smartcash.bitcoiner.me/smartnodes/calculator/")


        # BITCOINER SITE
        elif "bitcoiner" in message.content.lower():
            log_interaction(message)
            await client.send_message(message.channel, "https://smartcash.bitcoiner.me")


        # WINNERS
        elif "winners" in message.content.lower():
            log_interaction(message)
            await client.send_message(message.channel, "https://smartcash.bitcoiner.me/smartnodes/payouts/")


        # HELP
        elif "help" in message.content.lower():
            log_interaction(message)
            await client.send_message(message.channel, "You can @mention or DM " + supportbot_id + ''' and say things containing phrases like:

**clear log**: I will tell you what I know about clearing your SmartNode's `debug.log` file. 
**smartnode payout**: I will tell you what I know about SmartNode payouts.
**smartrewards check [address]**: I will try to determine whether or not the provided address is eligible in this round of SmartRewards (this feature is beta!).
**smartrewards**: I will tell you what I know about SmartRewards.
**smarthive voting**: I will tell you what I know about SmartHive voting.
**expired OR new_start**: I will tell you what I know about the different SmartNode status messages.
**upgrade**: I will tell you what I know about updating your SmartNode.
**install.sh**: I will provide the link to the official SmartNode install scripts.
**smartnode monitor**: I will provide the link to the SmartNode Monitoring service.
**guide**: I will provide the link to the official SmartNode install guides.
**troubleshooting**: I provide a link to a general SmartNode troubleshooting guide. 
**bootstrap**: I will provide the links to the different bootstrap files and instructions.
**chart**: I will provide the link to the SmartNode count chart.
**calculator**: I will provide the link to Bitcoiner's SmartNode return calculator.
**bitcoiner**: I will provide the link to Bitcoiner's site.
**winners**: I will provide the link to the SmartNode previous payments page.
**help**: I will show this message.

If you have any feedback, please provide it to my handler ''' + andrew_id + ". If you find me helpful, consider tipping me.")


        # Catchall
        else:
            log_interaction(message)
            await client.send_message(message.channel, "I'm afraid I don't understand, {0.author.mention}. You might try sending `help`.".format(message))


def get_address(address):
    transactions = []
    url = "https://explorer3.smartcash.cc/ext/getaddress/" + address
    response = requests.get(url)
    json_response = json.loads(response.text)

    balance = float(json_response["balance"])

    for tx in json_response["last_txs"]:
        transactions.append(tx)

    return balance,transactions


def walk_backwards(address,balance,transactions):
    now = datetime.datetime.utcnow()
    month = now.month
    day = now.day
    if day <= 25 and now.hour <= 7:
        month = 12 if (month -1 == 0) else month -1
        snapshot = (datetime.datetime(2018,month,25,7,0,tzinfo=timezone.utc))
        print(snapshot,flush=True)
        snapshot = snapshot.timestamp()
    else:
        snapshot = (datetime.datetime(2018,month,25,7,0,tzinfo=timezone.utc))
        print(snapshot,flush=True)
        snapshot = snapshot.timestamp()
    balance = float(balance)
    balance_at_snap = balance
    for transaction in transactions:
        transaction = transaction["addresses"]
        url = "https://explorer3.smartcash.cc/api/getrawtransaction?txid=" + transaction + "&decrypt=1"
        response = requests.get(url)
        json_response = json.loads(response.text)
        if int(json_response["time"]) >  snapshot:
            for tx in json_response["vout"]:
                if address in tx["scriptPubKey"]["addresses"]:
                    balance_at_snap -= float(tx["value"])
            break
    return balance_at_snap


def get_outgoing_timestamps(transactions):

    outgoing_times = []

    for transaction in transactions:
        if transaction["type"] == "vin":
            transaction = transaction["addresses"]
        else:
            continue
        #transaction.encode('utf8')
        url = "https://explorer3.smartcash.cc/api/getrawtransaction?txid=" + transaction + "&decrypt=1"
        response = requests.get(url)
        json_response = json.loads(response.text)
        outgoing_times.append(json_response["time"])

    return outgoing_times


def check_validity(balance,outgoing_times):
    now = datetime.datetime.utcnow()
    month = now.month
    day = now.day
    payout_month = 1 if (month + 1 == 13) else month + 1
    payout = str(payout_month) + "/25 at 7:00 UTC"
    if day <= 25 and now.hour <= 7:
        month = 12 if (month -1 == 0) else month -1
        snapshot = (datetime.datetime(2018,month,25,7,0,tzinfo=timezone.utc))
        print(snapshot,flush=True)
        snapshot = snapshot.timestamp()
    else:
        snapshot = (datetime.datetime(2018,month,25,7,0,tzinfo=timezone.utc))
        snapshot = snapshot.timestamp()
    if int(balance) < 1000:
        valid = False
        return valid,"it holds less than 1,000 SMART"
    else:
        valid = True
        reason = None
    for outgoing_time in outgoing_times:
        if int(outgoing_time) > snapshot:
            valid = False
            reason = "there was an outgoing transaction after the snapshot"
            break
        else:
            valid = True
            reason = None

    return valid,reason,payout

client.run('KEY')
#client.run('KEY', bot=False)

