// my_summarizer/static/js/main.js

// Wait until the DOM is fully loaded
document.addEventListener("DOMContentLoaded", function() {
    const summaryForm   = document.getElementById("summaryForm");
    const submitBtn     = document.getElementById("submitBtn");
    const progressMsg   = document.getElementById("inProgressMsg");
    const summaryDiv    = document.getElementById("stream_summary");
    const titleDiv      = document.getElementById("stream_title");
  
    if (!summaryForm) {
      // If we're not on the index page (where the form is), we can safely return.
      return;
    }
  
    // Attach a submit event listener to the form
    summaryForm.addEventListener("submit", function(e) {
      e.preventDefault();
  
      // Grab user inputs
      const videoUrl   = document.getElementById("video_url").value.trim();
      const modelName  = document.getElementById("model_name").value;
      const promptId   = document.getElementById("prompt_id").value;
  
      // Clear any previous streaming output
      summaryDiv.textContent = "";
      titleDiv.textContent   = "";
  
      // Disable the button + show "in progress" message
      if (submitBtn) {
        submitBtn.disabled = true;
      }
      if (progressMsg) {
        progressMsg.style.display = "block";
      }
  
      // Fire off a POST request to our SSE endpoint
      fetch("/api/summarize_stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          url: videoUrl,
          model: modelName,
          prompt_id: promptId
        })
      })
      .then(response => {
        if (!response.ok) {
          // If the server responds with 4xx or 5xx
          throw new Error("Network response was not OK");
        }
        // We'll read the body as a stream of text lines
        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let partial = "";
  
        // Recursive function to read each chunk
        function readChunk() {
          return reader.read().then(({ done, value }) => {
            if (done) {
              // No more data
              return;
            }
            // Decode current chunk
            partial += decoder.decode(value, { stream: true });
  
            // SSE blocks end with a blank line, parse them
            const lines = partial.split(/\r?\n/);
            partial = ""; // we'll rebuild partial from leftover lines
  
            let buffer = [];
            for (let i = 0; i < lines.length; i++) {
              const line = lines[i];
              if (line.startsWith("event: ") || line.startsWith("data: ")) {
                buffer.push(line);
              } else if (line === "") {
                // End of an SSE block
                handleSSEBlock(buffer.join("\n"));
                buffer = [];
              } else {
                buffer.push(line);
              }
            }
            // leftover lines that didn't form a complete block
            partial = buffer.join("\n");
  
            return readChunk();  // keep reading
          });
        }
        return readChunk();
      })
      .catch(err => {
        // If network error or something else fails
        console.error("Fetch error:", err);
        summaryDiv.textContent = "Error: " + err.message;
        // Re-enable the button
        if (submitBtn) {
          submitBtn.disabled = false;
        }
        if (progressMsg) {
          progressMsg.style.display = "none";
        }
      });
    });
  
    // Helper to handle an SSE block of lines
    function handleSSEBlock(block) {
      // block could have lines like:
      // event: SUMMARY_CHUNK
      // data: some partial text
      // or event: TITLE_CHUNK
      // data: partial text
      // or event: DONE
      // data: ok
      // or event: ERROR
      const lines = block.split("\n");
      let eventName = null;
      let dataValue = "";
  
      for (let ln of lines) {
        if (ln.startsWith("event: ")) {
          eventName = ln.substring(7).trim(); // e.g. SUMMARY_CHUNK
        } else if (ln.startsWith("data: ")) {
          dataValue = ln.substring(6); // e.g. partial token
        }
      }
  
      if (!eventName) return;
  
      if (eventName === "SUMMARY_CHUNK") {
        // Append partial token to the summary div
        summaryDiv.textContent += dataValue;
      }
      else if (eventName === "TITLE_CHUNK") {
        // Append partial token to the title div
        titleDiv.textContent += dataValue;
      }
      else if (eventName === "DONE") {
        // Summarizing is finished; reload to see new record in the table
        window.location.reload();
      }
      else if (eventName === "ERROR") {
        // Show the error message, re-enable the button
        summaryDiv.textContent += "\nERROR: " + dataValue + "\n";
        if (submitBtn) {
          submitBtn.disabled = false;
        }
        if (progressMsg) {
          progressMsg.style.display = "none";
        }
      }
    }
  });
  