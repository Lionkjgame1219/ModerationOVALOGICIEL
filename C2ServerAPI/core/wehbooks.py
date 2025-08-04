import discord
from discord import SyncWebhook, Embed
import datetime

webhook = SyncWebhook.from_url("METTRE LE LIEN DE VOTRE WEHBOOKs")

def MessageForAdmin(user_id, username, reason, duration_or_msg, categorie):
    with open("admin_pseudo.txt", 'r', encoding="utf-8") as f:
        moderator_id = f.read().strip()

    embed = Embed(
        title="🔔 Action administrative",
        color=0xF52D05,
        timestamp=datetime.datetime.utcnow()
    )


    if categorie == "ban":
        embed.description = "Un **bannissement** a été effectué"
        embed.add_field(
            name="Informations",
            value=f"\nID: {user_id}\nPseudo: {username}\nRaison: {reason}\nDurée: {duration_or_msg}h",
            inline=False
        )

    elif categorie == "unban":
        embed.description = "Un **débannissement** a été effectué"
        embed.add_field(
            name="Informations",
            value=f"\nID: {user_id}",
            inline=False
        )


    elif categorie == "kick":
        embed.description = "Un **kick** a été effectué"
        embed.add_field(
            name="Informations",
            value=f"\nID: {user_id}\nPseudo: {username}\nRaison: {reason}",
            inline=False
        )

    elif categorie == "adminsay":
        embed.description = "Un **message administrateur** a été envoyé"
        embed.add_field(name="Message", value=f"```{reason}```", inline=False)

    elif categorie == "serversay":
        embed.description = "Un **message serveur** a été envoyé"
        embed.add_field(name="Message", value=f"```{reason}```", inline=False)

    elif categorie == "time":
        embed.description = "Un **temps** a été ajouté au joueur"
        embed.add_field(name="Détails", value=f"```txt\nID: {user_id}\nDurée ajoutée: {duration_or_msg} minutes```", inline=False)

    embed.add_field(name="Modérateur", value=f"<@{moderator_id}>", inline=False)
    embed.set_footer(text="Interface Admin")

    webhook.send(username="Admin Bot", embed=embed)

