#!/bin/bash

# Set your API key
GROQ_API_KEY="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"

# Directory containing .txt files
DIR_PATH="./transform"

# Function to process each file
process_file() {
  local file="$1"
  
  # Read and escape the content of the file using jq
  CONTENT=$(jq -Rs '.' < "$file")

  # Create a new filename for the JSON output
  BASE_NAME=$(basename "$file" .txt)
  OUTPUT_FILE="$DIR_PATH/Zusammenfassung - $BASE_NAME.json"

  # Send the curl request and save the full response in a temporary file
  RESPONSE=$(curl -s "https://api.groq.com/openai/v1/chat/completions" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $GROQ_API_KEY" \
    -d "{
          \"messages\": [
            {
              \"role\": \"system\",
              \"content\": \"Wähle einen umfassenden Titel als string 'titel', fasse das Thema der Vorlesung aus Analysis 1 und Lineare Algebra stichpunktartig kurz zusammen, etwa zwei Sätze als string 'thema' und gebe 3-10 Tags als array mit strings 'tags', außerdem gebe den array 'wichtig' mit strings, in die wichtigen Definitionen oder Gleichungen aufgelistet sind, die in dieser Vorlesung vorkommen, so dass sie kurz sind aber ohne Kontext verstanden werden können.\nalles in JSON\"
            },
            {
              \"role\": \"user\",
              \"content\": $CONTENT
            }
          ],
          \"model\": \"llama-3.1-70b-versatile\",
          \"temperature\": 0.88,
          \"max_tokens\": 1024,
          \"top_p\": 1,
          \"stream\": false,
          \"response_format\": {
            \"type\": \"json_object\"
          },
          \"stop\": null
        }")

  # Extract the unescaped message content from the response using jq
  MESSAGE=$(echo "$RESPONSE" | jq -r '.choices[0].message.content')

  # Save the extracted message content to the output file
  echo "$MESSAGE" > "$OUTPUT_FILE"

  echo "Saved response to $OUTPUT_FILE"
}

# Loop through all .txt files in the directory and process them one by one
for file in "$DIR_PATH"/*.txt; do
  process_file "$file"
  
  # Sleep for 60 seconds to handle rate limits
  echo "Waiting 60 seconds due to rate limits..."
  sleep 40
done

