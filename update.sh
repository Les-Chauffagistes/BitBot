#!/bin/bash

PLIST_PATH="/Library/LaunchDaemons/com.bot.bitbot.plist"
LABEL="com.bot.bitbot"
CODE_DIR="/usr/local/bin/BitBot"

set -e  # stoppe le script si une commande échoue

echo "==> Vérification du statut du service..."
if sudo launchctl list | grep -q "$LABEL"; then
    echo "Arrêt du service..."
    sudo launchctl unload "$PLIST_PATH" || { echo "Échec du déchargement."; exit 1; }
else
    echo "Le service n'était pas actif."
fi

echo "==> Mise à jour du code..."
cd "$CODE_DIR" || { echo "Impossible d'accéder au dossier $CODE_DIR."; exit 1; }

git fetch origin || { echo "Échec du fetch."; exit 1; }
git reset --hard origin/develop || { echo "Échec du reset."; exit 1; }

echo "==> Lancement des tests..."
if ! venv/bin/python -m pytest -q; then
    echo "Tests échoués ❌, rollback au commit précédent..."
    git reset --hard HEAD@{1}  # revient au commit précédent
    sudo launchctl load "$PLIST_PATH"  # relance l’ancienne version
    exit 1
fi

echo "==> Tests réussis ✅, redémarrage du service..."
sudo launchctl load "$PLIST_PATH" || { echo "Échec du rechargement."; exit 1; }

echo "==> Mise à jour et redémarrage terminés avec succès."