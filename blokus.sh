#!/bin/bash
# Blokus Server Manager
# Usage: ./blokus.sh [start|stop|restart|status|logs]

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PID_FILE="$SCRIPT_DIR/.blokus.pid"
BACKEND_PORT=8000
FRONTEND_PORT=5500

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { printf "${BLUE}ℹ${NC}  $1\n"; }
log_success() { printf "${GREEN}✓${NC}  $1\n"; }
log_error() { printf "${RED}✗${NC}  $1\n"; }
log_warning() { printf "${YELLOW}⚠${NC}  $1\n"; }

is_running() {
    if [ -f "$PID_FILE" ]; then
        BPID=$(sed -n '1p' "$PID_FILE")
        FPID=$(sed -n '2p' "$PID_FILE")
        if [ -n "$BPID" ] && kill -0 "$BPID" 2>/dev/null && [ -n "$FPID" ] && kill -0 "$FPID" 2>/dev/null; then
            return 0
        fi
    fi
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1 || lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    fi
    return 1
}

start() {
    if is_running; then
        log_warning "Servers (or ports) are already in use. Run './blokus.sh stop' first."
        exit 0
    fi
    log_info "Starting Blokus servers..."
    source "$SCRIPT_DIR/blokus-engine/.venv/bin/activate"
    
    cd "$SCRIPT_DIR/blokus-server"
    nohup python main.py > "$SCRIPT_DIR/.blokus-backend.log" 2>&1 &
    BPID=$!
    
    sleep 2
    
    cd "$SCRIPT_DIR/blokus-web"
    nohup python -m http.server $FRONTEND_PORT > "$SCRIPT_DIR/.blokus-frontend.log" 2>&1 &
    FPID=$!
    
    echo "$BPID" > "$PID_FILE"
    echo "$FPID" >> "$PID_FILE"
    
    log_success "Servers started! UI: http://localhost:$FRONTEND_PORT"
}

stop() {
    log_info "Stopping Blokus servers..."
    if [ -f "$PID_FILE" ]; then
        BPID=$(sed -n '1p' "$PID_FILE" 2>/dev/null)
        FPID=$(sed -n '2p' "$PID_FILE" 2>/dev/null)
        
        if [ -n "$BPID" ]; then kill "$BPID" 2>/dev/null || true; fi
        if [ -n "$FPID" ]; then kill "$FPID" 2>/dev/null || true; fi
        
        rm "$PID_FILE"
    fi
    
    PIDS=$(lsof -ti :$BACKEND_PORT,$FRONTEND_PORT 2>/dev/null)
    if [ -n "$PIDS" ]; then
        kill -9 $PIDS 2>/dev/null || true
    fi
    log_success "Servers stopped and ports cleared."
}

case "${1:-}" in
    start) start ;;
    stop) stop ;;
    restart) stop; sleep 1; start ;;
    status) 
        if is_running; then log_success "Running"; else log_warning "Stopped"; fi 
        ;;
    logs)
        tail -n 20 "$SCRIPT_DIR"/.blokus-*.log 2>/dev/null || log_warning "No logs found"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
