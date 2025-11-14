#!/bin/bash

if [ -d "data" ]; then
    echo "Data folder $DATA_DIR aleady created. Stopping setup."
    read -n 1
    exit 1
fi

# Créer les répertoires
echo "Creating directories..."
mkdir -p "data/business/auctions"
mkdir -p "data/business/images"
mkdir -p "data/business/sales"
mkdir -p "data/business/shop"
mkdir -p "data/business/vault"
mkdir -p "data/wallets/pi"
mkdir -p "data/wallets/bitcoin"

# Créer les fichiers
echo "Creating files..."
touch "data/.env"
touch "data/business/history.json"
touch "data/business/signin_channels.json"
touch "data/wallets/bitcoin_lnurl_ids.json"
touch "data/wallets/pi_blacklist_payments.json"
touch "data/wallets/pi_notified_payments.json"
touch "data/wallets/pi_pending_payments.json"

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