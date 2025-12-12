#!/bin/bash

# Ports to check
PORTS=(8000 3000)

# Color codes
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

write_info() {
    echo -e "${CYAN}[INFO] $1${NC}"
}

write_success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

write_warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Kill esbuild processes
write_info "Killing esbuild processes..."


write_info "Searching for processes using ports: ${PORTS[*]}"

any_processes_found=false

for port in "${PORTS[@]}"; do
    # Use netstat to find processes on Windows (Git Bash)
    pids=$(netstat -ano | grep ":$port " | grep "LISTENING" | awk '{print $5}' | sort -u)

    if [ -n "$pids" ]; then
        any_processes_found=true
        for pid in $pids; do
            # Get process name using tasklist
            process_name=$(tasklist //FI "PID eq $pid" //FO CSV //NH 2>/dev/null | cut -d',' -f1 | tr -d '"')

            if [ -n "$process_name" ] && [ "$process_name" != "INFO: No tasks are running which match the specified criteria." ]; then
                write_info "Found process $process_name (PID: $pid) using port $port"

                # Kill the process
                if taskkill //PID "$pid" //F 2>/dev/null; then
                    write_success "Successfully terminated process $process_name (PID: $pid)"
                else
                    write_warning "Failed to terminate process $process_name (PID: $pid)"
                fi
            fi
        done
    fi
done

if [ "$any_processes_found" = false ]; then
    write_info "No processes found using the specified ports."
fi