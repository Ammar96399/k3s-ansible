CPU_METHODS=("union")
STRESS_TEST_LOG="/home/kazem/benchmark/results/start_end_time.csv"

initialize_log_file() {
    if [ ! -f "$STRESS_TEST_LOG" ]; then
        echo "cpu_method,load,start_time,end_time" > "$STRESS_TEST_LOG"
    fi
}

perform_stress_test() {
    for i in {0..0}; do 
        CPU_METHOD=${CPU_METHODS[$i]}

        echo "Stress testing with $CPU_METHOD ..."
        for LOAD in 0 10 20 30 40 50 60 70 80 90 100; do
            START_TIME=$(date +%s)
            echo "Stressing at $LOAD%"
            stress-ng -c 0 -l $LOAD -t 300s --cpu-method "$CPU_METHOD"
            END_TIME=$(date +%s)
            
            # Log the start and end times in Unix time
            echo "$CPU_METHOD,$LOAD,$START_TIME,$END_TIME" >> "$STRESS_TEST_LOG"
            
            sleep 60
        done
    done
}

initialize_log_file

perform_stress_test

echo "Main script finished."