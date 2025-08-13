#!/bin/bash
set -e

# Function to log with timestamp
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

# Function to check if all required environment variables are set
check_env_vars() {
    local required_vars=("API_KEY" "API_SECRET" "EXCHANGE")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log "ERROR: Missing required environment variables: ${missing_vars[*]}"
        log "Please set these variables in your .env file or pass them to Docker"
        exit 1
    fi
}

# Function to validate configuration
validate_config() {
    log "Validating configuration..."
    
    # Check if API keys look like placeholders
    if [[ "$API_KEY" == *"your_api_key_here"* ]] || [[ "$API_KEY" == *"placeholder"* ]]; then
        log "WARNING: API_KEY appears to be a placeholder value"
    fi
    
    if [[ "$API_SECRET" == *"your_api_secret_here"* ]] || [[ "$API_SECRET" == *"placeholder"* ]]; then
        log "WARNING: API_SECRET appears to be a placeholder value"
    fi
    
    # Validate exchange
    case "$EXCHANGE" in
        binance|gate)
            log "Exchange set to: $EXCHANGE"
            ;;
        *)
            log "WARNING: Unsupported exchange: $EXCHANGE"
            ;;
    esac
    
    # Validate dry run mode
    if [[ "${DRY_RUN:-true}" == "true" ]]; then
        log "Running in DRY RUN mode - no real trades will be executed"
    else
        log "WARNING: DRY RUN disabled - real trades will be executed!"
    fi
}

# Function to test imports
test_imports() {
    log "Testing Python imports..."
    python -c "
import sys
try:
    import main
    from constants import *
    from config_validator import ConfigValidator
    print('✅ All imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
"
}

# Main execution
main() {
    log "Starting Volume Bot Docker Container"
    log "======================================"
    
    # Check required environment variables
    check_env_vars
    
    # Validate configuration
    validate_config
    
    # Test imports
    test_imports
    
    log "Configuration validated successfully"
    log "Starting volume bot..."
    
    # Execute the main command
    exec "$@"
}

# Run main function with all arguments
main "$@"