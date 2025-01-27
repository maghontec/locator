#!/bin/bash

echo "Checking environment for Nigerian Healthcare Facilities Explorer..."
echo "----------------------------------------"

# Check Python version
python_version=$(python3 --version 2>&1)
echo "Python Version: $python_version"

# Check if required environment variables are set
echo -e "\nChecking environment variables:"
vars=("DATABASE_URL" "PGUSER" "PGPASSWORD" "PGHOST" "PGPORT" "PGDATABASE")
missing_vars=0

for var in "${vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ $var is not set"
        missing_vars=$((missing_vars + 1))
    else
        echo "✅ $var is set"
    fi
done

# Check PostgreSQL connection
echo -e "\nTesting PostgreSQL connection:"
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL client is installed"
else
    echo "❌ PostgreSQL client is not installed"
fi

# Summary
echo -e "\nEnvironment Check Summary:"
if [ $missing_vars -eq 0 ]; then
    echo "✅ All required environment variables are set"
else
    echo "❌ $missing_vars environment variables are missing"
fi

echo -e "\nFor deployment instructions, please refer to README.md"
