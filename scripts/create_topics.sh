#!/usr/bin/env bash
BOOTSTRAP=localhost:9092

topics=(A_input A_output B_input B_output C_input C_output D_input D_input_ready)

for t in "${topics[@]}"; do
  docker compose exec kafka /bin/kafka-topics \
    --create --if-not-exists --topic "$t" \
    --partitions 3 --replication-factor 1 \
    --bootstrap-server "$BOOTSTRAP"
done
echo "✅  All topics created."