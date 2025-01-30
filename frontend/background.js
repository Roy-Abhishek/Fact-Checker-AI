chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "highlightedTextAction",
    title: "Analyze/Verify Highlighted Text",
    contexts: ["selection"],
  });
});

chrome.contextMenus.onClicked.addListener((info) => {
    if (info.menuItemId === "highlightedTextAction" && info.selectionText) {
        const selectedText = encodeURIComponent(info.selectionText);
    
        // Open the new tab and pass the selected text as a query parameter
        chrome.tabs.create({
          url: `left_click.html?selectedText=${selectedText}`
        });
    }
});
