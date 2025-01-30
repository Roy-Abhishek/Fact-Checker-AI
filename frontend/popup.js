document.addEventListener("DOMContentLoaded", async () => {
  // Parse the query parameters from the URL
  const urlParams = new URLSearchParams(window.location.search);
  const selectedText = urlParams.get("selectedText");

  // Getting the result text.
  const result = await fetchAnalysis(decodeURIComponent(selectedText));

  // Display the selected text
  const output = document.getElementById("output");
  if (selectedText) {
    output.innerText = result;
  } else {
    output.innerText = "No text was selected.";
  }
});

async function fetchAnalysis(claims) {
  for (let i = 0; i < 2; i++) {
    try {
      // 1. Make a request to the API
      const response = await fetch('http://helloraspy.duckdns.org:4001/analysis/' + claims);
      
      // 2. Check if the response is successful (status code in the 200–299 range)
      if (!response.ok) {
        if (i === 2) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        continue;
      }
      
      // // 3. Parse the JSON body of the response
      const data = await response.json()
      
      // You can return the data to be used elsewhere
      return data["result"];

    } catch (error) {
      // 5. Handle any errors
      console.error('Error fetching data:', error);
    }
  }
}


