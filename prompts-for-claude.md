# MCP Test Prompts for Claude Desktop 🧪

**Quick Reference for Testing Alfresco MCP Server with Claude Desktop**

Copy and paste these prompts into Claude Desktop to systematically test all MCP server functionality. Make sure your Alfresco MCP Server is running on `http://127.0.0.1:8003/mcp/` before testing.

---

## 🔧 **TOOL TESTING** (15 Tools)

### **1. Search Content Tool** (AFTS - Alfresco Full Text Search)
```
I need to search for documents in Alfresco. Can you search for:
- Documents containing "test"  
- Maximum 5 results
```

**Expected:** List of matching documents or "no results found" message

---

### **2. Browse Repository Tool**
```
Can you show me what's in the Alfresco repository user home -my- directory? I want to see what folders and files are available.
```

**Expected:** List of folders/files in repository root with names, types, and IDs

---

### **3. Create Folder Tool**
```
Please create a new folder called "Claude_Test_Folder" in the repository shared folder (-shared-) with the description "Folder created during Claude MCP testing".
```

**Expected:** Success message with new folder ID, or error if folder already exists

---

### **4. Upload Document Tool**
```
I want to upload a simple text document. Please create a file called "claude_test_doc.txt" in the repository shared folder with this content:

"This is a test document created by Claude via MCP.
Created: [current date/time]
Purpose: Testing Alfresco MCP Server functionality
Status: Active"

Use the description "Test document uploaded via Claude MCP"
```

**Expected:** Success message with document ID and upload confirmation

---

### **5. Get Node Properties Tool**
```
Can you get the properties and metadata for the document we just uploaded? Use the node ID from the previous upload.
```

**Expected:** Full property list including name, type, created date, size, etc.

---

### **6. Update Node Properties Tool**
```
Please update the properties of that document to add:
- Title: "Claude MCP Test Document"
- Description: "Updated via Claude MCP testing session"

```

**Expected:** Success message confirming property updates

---

### **7. Download Document Tool**
```
Now download the content of that test document we created to verify it was uploaded correctly.
```

**Expected:** Base64 encoded content that matches what we uploaded

---

### **8. Checkout Document Tool**
```
Please checkout the test document for editing. This should lock it so others can't modify it while we're working on it.
```

**Expected:** Success message indicating document is checked out/locked

---

### **9. Checkin Document Tool**
```
Check the document back in as a minor version with the comment "Updated via Claude MCP testing - minor revision".
```

**Expected:** Success message with new version number

---

### **10. Cancel Checkout Tool** 
```
If you have any documents currently checked out, please cancel the checkout for one of them to test this functionality. Use the node ID of a checked-out document.
```

**Expected:** Success message confirming checkout cancellation

---

### **11. Advanced Search Tool**
```
Test the advanced search with multiple filters:
- Search for documents created after "2024-01-01"
- Content type: "pdf" 
- Node type: "cm:content"
- Maximum 10 results

Show me how advanced filtering works compared to basic search.
```

**Expected:** Filtered search results based on multiple criteria

---

### **12. Search by Metadata Tool**
```
Search for documents by specific metadata:
- Property name: "cm:title"
- Property value: "test" 
- Comparison: "contains"
- Node type: "cm:content"

This should find documents where the title contains "test".
```

**Expected:** Documents matching the metadata criteria

---

### **13. CMIS Search Tool** (SQL-like Queries)
```
Test CMIS SQL-like searching with these examples:

1. First, try a preset: use "recent_documents" to see the most recently created documents
2. Then try a custom CMIS query: "SELECT * FROM cmis:document WHERE cmis:name LIKE 'test%'"
3. (Doesn't work) Search for PDF files only: "SELECT * FROM cmis:document WHERE cmis:contentStreamMimeType = 'application/pdf'"
4. (This works) Search for PDF files only "SELECT * FROM cmis:document WHERE cmis:name LIKE '%.pdf'"

Compare CMIS structured results with AFTS full-text search operators.
```

**Expected:** SQL-style structured results with precise metadata filtering

---

### **14. Delete Node Tool** (Use with caution!)
```
Finally, let's clean up by deleting the test document we created. Please delete the test document (but keep the folder for now).
```

**Expected:** Success message confirming deletion

---

## 🔍 **SEARCH COMPARISON TESTING**

### **Compare All 4 Search Tools**
```
Help me understand the differences between the four search methods:

1. Use basic search_content to find documents containing "test" (AFTS full-text search)
2. Use advanced_search with multiple filters (created after 2024-01-01, content type pdf) (AFTS with filters)  
3. Use search_by_metadata to find documents where cm:title contains "test" (AFTS property search)
4. Use cmis_search with SQL query "SELECT * FROM cmis:document WHERE cmis:name LIKE 'test%'" (CMIS SQL)

Compare the results and explain when to use each search method.
```

**Expected:** Clear comparison showing AFTS vs CMIS capabilities and different search approaches

---

## 🗄️ **CMIS ADVANCED TESTING**

### **CMIS Preset Exploration**
```
Test all the CMIS presets to understand different query types:

1. Use preset "recent_documents" to see newest content
2. Use preset "large_files" to find documents over 1MB
3. Use preset "pdf_documents" to find all PDF files
4. Use preset "word_documents" to find Word documents

Show me what each preset reveals about the repository structure.
```

**Expected:** Different categories of content with SQL-precision filtering

---

### **Custom CMIS Queries**
```
Test custom CMIS SQL queries for advanced scenarios:

1. Find documents created today: "SELECT * FROM cmis:document WHERE cmis:creationDate > '2024-01-01T00:00:00.000Z'"
2. Find large PDFs: "SELECT * FROM cmis:document WHERE cmis:contentStreamMimeType = 'application/pdf' AND cmis:contentStreamLength > 500000"
3. Find folders with specific names: "SELECT * FROM cmis:folder WHERE cmis:name LIKE '%test%'"

This demonstrates CMIS's SQL-like precision for complex filtering.
```

**Expected:** Precise, database-style results showing CMIS's structured query power

---

## 📝 **PROMPT TESTING** (1 Prompt)

### **Search and Analyze Prompt**
```
Can you use the search_and_analyze prompt to help me find and analyze documents related to "project management" in the repository? I want to understand what content is available and get insights about it.
```

**Expected:** Structured analysis with search results, content summary, and insights

---

## 📦 **RESOURCE TESTING** (5 Resources)

### **1. Repository Info Resource**
```
Can you check the repository information resource to tell me about this Alfresco instance? I want to know version, edition, and basic details.
```

**Expected:** Repository version, edition, schema info

---

### **2. Repository Health Resource**
```
Please check the repository health status. Is everything running normally?
```

**Expected:** Health status indicating if services are up/down

---

### **3. Repository Stats Resource**
```
Show me the current repository statistics - how many documents, users, storage usage, etc.
```

**Expected:** Usage statistics and metrics

---

### **4. Repository Config Resource**
```
Can you check the repository configuration details? I want to understand how this Alfresco instance is set up.
```

**Expected:** Configuration settings and parameters

---

### **5. Dynamic Repository Resource**
```
Can you check the "users" section of repository information to see what user management details are available?
```

**Expected:** User-related repository information

---

## 🚀 **COMPLEX WORKFLOW TESTING**

### **Complete Document Lifecycle**
```
Let's test a complete document management workflow:

1. Create a folder called "Project_Alpha"
2. Upload a document called "requirements.md" to that folder with some project requirements content
3. Get the document properties to verify it was created correctly
4. Update the document properties to add a title and description
5. Checkout the document for editing
6. Checkin the document as a major version with appropriate comments
7. Search for documents containing "requirements" using basic search (AFTS full-text)
8. Try advanced search with date filters to find the same document (AFTS with filters)
9. Use metadata search to find it by title property (AFTS property search)
10. Use CMIS search with SQL query to find it by name (CMIS SQL)
11. Download the document to verify content integrity

Walk me through each step and confirm success before moving to the next.
```

**Expected:** Step-by-step execution with confirmation at each stage

---

### **Repository Exploration**
```
Help me explore this Alfresco repository systematically:

1. Check repository health and info first
2. Browse the root directory to see what's available
3. Search for any existing content
4. Show me repository statistics
5. Summarize what you've learned about this Alfresco instance

Provide a comprehensive overview of what we're working with.
```

**Expected:** Comprehensive repository analysis and summary

---

## 🐛 **ERROR TESTING**

### **Invalid Operations**
```
Let's test error handling:

1. Try to download a document with invalid ID "invalid-node-id"
2. Try to delete a non-existent node
3. Try to upload a document with missing required parameters
4. Search with an empty query

Show me how the MCP server handles these error cases.
```

**Expected:** Graceful error messages without crashes

---

### **Authentication Testing**
```
Can you verify that authentication is working properly by:

1. Checking repository info (requires read access)
2. Creating a test folder (requires write access)  
3. Deleting that folder (requires delete access)

This will confirm all permission levels are working.
```

**Expected:** All operations succeed, confirming proper authentication

---

## 📊 **PERFORMANCE TESTING**

### **Batch Operations**
```
Test performance with multiple operations:

1. Create 3 folders with names "Batch_Test_1", "Batch_Test_2", "Batch_Test_3"
2. Upload a small document to each folder
3. Search for "Batch_Test" to find all created content
4. Clean up by deleting all test content

Monitor response times and any issues with multiple rapid operations.
```

**Expected:** All operations complete successfully with reasonable response times

---

## ✅ **SUCCESS CRITERIA**

For a fully functional MCP server, you should see:

- ✅ All 15 tools respond without errors (including new CMIS search)
- ✅ The search_and_analyze prompt works
- ✅ All 5 resources return data
- ✅ Authentication works for read/write/delete operations
- ✅ AFTS and CMIS search both work properly
- ✅ Error handling is graceful
- ✅ Complex workflows complete successfully
- ✅ Performance is acceptable

## 🔍 **TROUBLESHOOTING**

If tests fail:

1. **Check server status**: Verify MCP server is running on http://127.0.0.1:8003/mcp/
2. **Check Alfresco**: Ensure Alfresco is running on http://localhost:8080
3. **Check authentication**: Verify credentials in config.yaml
4. **Check logs**: Review server console output for errors
5. **Check network**: Ensure no firewall/proxy issues

## 📝 **LOGGING CLAUDE'S RESPONSES**

When testing, note:
- Which operations succeed/fail
- Any error messages received
- Response times for operations
- Quality of returned data
- Any unexpected behavior

This will help identify areas needing improvement in the MCP server implementation. 