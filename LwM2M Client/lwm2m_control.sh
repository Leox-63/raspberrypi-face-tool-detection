#!/bin/bash
# LwM2M Client Control Script

PROJECT_DIR="/home/pi/Desktop/Python_Proj/LwM2M Client"
PYTHON_CMD="python3"
MAIN_SCRIPT="main.py"
PID_FILE="/tmp/lwm2m_client.pid"
LOG_FILE="/tmp/lwm2m_client.log"

cd "$PROJECT_DIR"

case "$1" in
    start)
        if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
            echo "LwM2M Client is already running (PID: $(cat $PID_FILE))"
            exit 1
        fi
        
        echo "Starting LwM2M Client..."
        nohup $PYTHON_CMD $MAIN_SCRIPT > "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"
        echo "LwM2M Client started (PID: $!)"
        echo "Logs: $LOG_FILE"
        ;;
        
    stop)
        if [ ! -f "$PID_FILE" ]; then
            echo "LwM2M Client is not running"
            exit 1
        fi
        
        PID=$(cat "$PID_FILE")
        echo "Stopping LwM2M Client (PID: $PID)..."
        
        # Send SIGTERM for graceful shutdown
        kill -TERM $PID 2>/dev/null
        
        # Wait up to 10 seconds for graceful shutdown
        for i in {1..10}; do
            if ! kill -0 $PID 2>/dev/null; then
                break
            fi
            sleep 1
        done
        
        # Force kill if still running
        if kill -0 $PID 2>/dev/null; then
            echo "Force killing LwM2M Client..."
            kill -KILL $PID 2>/dev/null
        fi
        
        rm -f "$PID_FILE"
        echo "LwM2M Client stopped"
        ;;
        
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
        
    status)
        if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
            echo "LwM2M Client is running (PID: $(cat $PID_FILE))"
            echo "Logs: $LOG_FILE"
        else
            echo "LwM2M Client is not running"
            [ -f "$PID_FILE" ] && rm -f "$PID_FILE"
        fi
        ;;
        
    logs)
        if [ -f "$LOG_FILE" ]; then
            tail -f "$LOG_FILE"
        else
            echo "No log file found"
        fi
        ;;
        
    monitor)
        echo "Starting LwM2M Monitor..."
        echo "Press Ctrl+C to stop the monitor"
        
        # Trap SIGINT (Ctrl+C) to exit cleanly
        trap 'echo -e "\nMonitor stopped by user"; exit 0' INT
        
        $PYTHON_CMD monitor.py
        ;;
        
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|monitor}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the LwM2M client service"
        echo "  stop    - Stop the LwM2M client service"
        echo "  restart - Restart the LwM2M client service"
        echo "  status  - Show service status"
        echo "  logs    - Show and follow service logs"
        echo "  monitor - Start the sensor data monitor"
        exit 1
        ;;
esac
