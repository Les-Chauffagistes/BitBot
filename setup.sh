#!/bin/bash

# Créer les répertoires
echo "Creating directories..."
mkdir -p "data/wallets/bitcoin"
mkdir -p "data/output"

# Créer les fichiers
echo "Creating files..."
touch "data/.env"
touch "data/wallets/bitcoin_lnurl_ids.json"

if [ -d "data" ]; then
    echo "Data folder $DATA_DIR aleady created. Stopping setup."
    exit 1
fi

# Initialiser les fichiers de configuration
echo "Initializing configuration files..."
echo "DISCORD_API_TOKEN=\"\"" >> "data/.env"
echo "OPEN_NODE_WITHDRAW_API_KEY_=\"\"" >> "data/.env"
echo "OPEN_NODE_INVOICE_API_KEY_=\"\"" >> "data/.env"
echo "MODE=\"DEV\"" >> "data/.env"
echo "{}" >> "data/business/history.json"
echo "{}" >> "data/business/signin_channels.json"
echo "{}" >> "data/wallets/bitcoin_lnurl_ids.json"
echo "[]" >> "data/wallets/pi_blacklist_payments.json"
echo "[]" >> "data/wallets/pi_notified_payments.json"
echo "{}" >> "data/wallets/pi_pending_payments.json"

# Activer l'environnement virtuel
echo "Preparing virtual environment..."
python3.12 -m venv venv
source "venv/bin/activate"

# Mettre à jour pip et installer les dépendances
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Afficher un message de confirmation
echo "Setup completed."