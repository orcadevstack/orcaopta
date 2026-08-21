Write-Host "Installing Orcaopta environment..."

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create required folders
mkdir models -ErrorAction SilentlyContinue
mkdir data -ErrorAction SilentlyContinue

Write-Host "Environment setup complete."
