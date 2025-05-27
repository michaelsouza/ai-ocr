**2. Frontend Changes (`templates/index.html`)**

We need to add UI elements (add input, add button, remove buttons, save button) and JavaScript logic to handle adding, removing, and saving the file list.

**2.a. HTML Changes (Inside the "Files" Card):**

Modify the "Files" card structure like this:

```html
<!-- Inside <div class="col-md-4"> -->
<div class="card mb-3">
    <div class="card-header d-flex justify-content-between align-items-center">
        <span><i class="bi bi-file-earmark-code"></i> Files</span>
        <div>
            <!-- Existing Select/Clear Buttons -->
            <button type="button" class="btn btn-sm btn-outline-secondary me-1" id="selectAllFilesBtn"
                title="Select Visible Files">
                <i class="bi bi-check2-square"></i>
            </button>
            <button type="button" class="btn btn-sm btn-outline-secondary me-2" id="clearAllFilesBtn"
                title="Deselect Visible Files">
                <i class="bi bi-eraser"></i>
            </button>
            <!-- NEW Save Button -->
            <button type="button" class="btn btn-sm btn-outline-success" id="saveFilesBtn"
                title="Save changes to prompt_config.json" disabled>
                <i class="bi bi-save"></i> Save
            </button>
        </div>
    </div>
    <div class="card-body">
        <!-- NEW Add File Section -->
        <div class="input-group mb-3">
            <input type="text" id="newFilePathInput" class="form-control form-control-sm" placeholder="Add file path (relative to WD)">
            <button class="btn btn-outline-secondary btn-sm" type="button" id="addFileBtn" title="Add File to List">
                <i class="bi bi-plus-lg"></i> Add
            </button>
        </div>
        <!-- Existing Search Input -->
        <input type="text" id="search" class="form-control mb-2" placeholder="Search files..."
            aria-label="Search files">
        <!-- File List Container -->
        <div id="codeItems">
            {% for filename in data.files %}
            <div class="form-check code-item d-flex align-items-center justify-content-between mb-1">
                <div class="flex-grow-1 me-2"> <!-- Wrapper for label/checkbox -->
                    <input class="form-check-input" type="checkbox" name="files" value="{{ filename }}"
                        id="file-{{ loop.index }}">
                    <label class="form-check-label" for="file-{{ loop.index }}">
                        <i class="bi bi-file-earmark"></i> <span class="file-path-display">{{ filename }}</span>
                    </label>
                </div>
                 <!-- NEW Remove Button -->
                <button type="button" class="btn btn-sm btn-outline-danger remove-file-btn p-0 px-1" title="Remove from list">
                    <i class="bi bi-x-lg"></i>
                </button>
            </div>
            {% else %}
            <small class="text-muted" id="no-files-message">Load config to see files.</small>
            {% endfor %}
        </div>
    </div>
</div>
<!-- End Files Card -->
```

**Key HTML Changes:**

1.  **Save Button:** Added `<button id="saveFilesBtn">` in the card header, initially `disabled`.
2.  **Add File Section:** Added an `input-group` with `<input id="newFilePathInput">` and `<button id="addFileBtn">`.
3.  **File List Container:** Wrapped the loop content inside `<div id="codeItems">`. This makes it easier to target for adding/removing items and checking for emptiness. Also added an ID `no-files-message` to the placeholder text.
4.  **Remove Button:** Added `<button class="remove-file-btn">` next to each file item.
5.  **File Item Structure:** Slightly adjusted the `div.code-item` using flexbox (`d-flex`, `align-items-center`, `justify-content-between`) to better align the checkbox/label and the remove button. Wrapped the checkbox/label in a `div.flex-grow-1` to make it take up available space.

**2.b. JavaScript Changes (Inside `<script>` block):**

Add new functions and event listeners, and modify existing ones.

```javascript
<script>
    // ... (keep existing toastr options and helper functions: shortenPath, updateFileListItemDisplay, sortFileList, autoResizeTextarea) ...

    // --- NEW Helper ---
    // Function to enable/disable the save button and mark changes
    function setFileListDirty(isDirty) {
        const saveBtn = document.getElementById('saveFilesBtn');
        if (saveBtn) {
            saveBtn.disabled = !isDirty;
            // Optional: Add a visual cue like a small asterisk
            // const fileHeader = saveBtn.closest('.card-header').querySelector('span');
            // if (fileHeader) {
            //     fileHeader.textContent = fileHeader.textContent.replace(' *', '') + (isDirty ? ' *' : '');
            // }
        }
    }

    // --- NEW Helper ---
    // Function to create a new file list item element
    function createFileListElement(filePath, index) {
        const fileItem = document.createElement('div');
        fileItem.className = 'form-check code-item d-flex align-items-center justify-content-between mb-1';
        const escapedFilePath = filePath.replace(/"/g, '&quot;'); // Basic escaping for value

        fileItem.innerHTML = `
            <div class="flex-grow-1 me-2">
                <input class="form-check-input" type="checkbox" name="files" value="${escapedFilePath}" id="file-${index}">
                <label class="form-check-label" for="file-${index}">
                    <i class="bi bi-file-earmark"></i> <span class="file-path-display">${escapedFilePath}</span>
                </label>
            </div>
            <button type="button" class="btn btn-sm btn-outline-danger remove-file-btn p-0 px-1" title="Remove from list">
                <i class="bi bi-x-lg"></i>
            </button>`;

        // Add event listener for the new remove button immediately
        fileItem.querySelector('.remove-file-btn').addEventListener('click', handleRemoveFileClick);

        // Apply path shortening and tooltip
        updateFileListItemDisplay(fileItem);
        return fileItem;
    }


    // --- Modify updateUIWithData ---
    function updateUIWithData(data) {
        // ... (keep existing WD and Prompts updates) ...

        // Clear and update file list
        const codeItemsContainer = document.getElementById('codeItems');
        // Keep search and add sections if they exist
        const searchInput = document.getElementById('search');
        // const addFileSection = searchInput.previousElementSibling; // More robust selection needed if layout changes

        // Clear only file items, keep search/add
        codeItemsContainer.querySelectorAll('.code-item, #no-files-message').forEach(el => el.remove());


        const noFilesMsg = document.getElementById('no-files-message') || document.createElement('small');
        noFilesMsg.id = 'no-files-message';
        noFilesMsg.className = 'text-muted';
        noFilesMsg.textContent = 'No files found in config.';

        if (data.files && data.files.length > 0) {
            data.files.forEach((filename, index) => {
                // Use the new helper to create elements
                const fileElement = createFileListElement(filename, `loaded-${index + 1}`); // Use unique ID prefix
                codeItemsContainer.appendChild(fileElement);
            });
            sortFileList(); // Re-sort the new list
            if (noFilesMsg.parentNode === codeItemsContainer) {
                 codeItemsContainer.removeChild(noFilesMsg); // Remove 'no files' message if files were added
            }
        } else {
            // Add placeholder text if no files and it's not already there
             if (!codeItemsContainer.querySelector('#no-files-message')) {
                codeItemsContainer.appendChild(noFilesMsg);
            }
        }

        // Disable save button after loading config (state is clean)
        setFileListDirty(false);

        // Re-attach search listener if needed (should persist if not cleared above)
        // document.getElementById('search')?.addEventListener('keyup', handleSearchKeyup); // Usually persists
    }

    // --- Event Handlers ---
    // ... (keep handleSearchKeyup, handlePromptLinkClick) ...

    // --- NEW Event Handler ---
    function handleAddFileClick() {
        const input = document.getElementById('newFilePathInput');
        const filePath = input.value.trim().replace(/\\/g, '/'); // Normalize slashes
        const container = document.getElementById('codeItems');

        if (!filePath) {
            toastr.warning("Please enter a file path to add.");
            return;
        }

        // Check for duplicates (case-insensitive check might be better)
        const existingFiles = Array.from(container.querySelectorAll('.code-item input[name="files"]'))
                                    .map(input => input.value.toLowerCase());
        if (existingFiles.includes(filePath.toLowerCase())) {
            toastr.warning(`File "${filePath}" is already in the list.`);
            return;
        }

        // Remove 'no files' message if present
        const noFilesMsg = document.getElementById('no-files-message');
        if (noFilesMsg) noFilesMsg.remove();


        // Create and add the new element
        // Generate a somewhat unique ID (e.g., based on timestamp or count)
        const newIndex = `new-${Date.now()}`;
        const newElement = createFileListElement(filePath, newIndex);
        container.appendChild(newElement);

        input.value = ''; // Clear input field
        sortFileList();
        setFileListDirty(true); // Mark changes as unsaved
        toastr.info(`File "${shortenPath(filePath)}" added to list. Remember to Save.`, "File Added");
    }

     // --- NEW Event Handler ---
    function handleRemoveFileClick(event) {
        const button = event.currentTarget;
        const fileItem = button.closest('.code-item'); // Find the parent div
        const filePath = fileItem.querySelector('input[name="files"]').value;

        if (fileItem) {
            fileItem.remove();
            toastr.info(`File "${shortenPath(filePath)}" removed from list. Remember to Save.`, "File Removed");
            setFileListDirty(true); // Mark changes as unsaved

             // Add 'no files' message back if the list is now empty
            const container = document.getElementById('codeItems');
            if (!container.querySelector('.code-item')) {
                const noFilesMsg = document.createElement('small');
                noFilesMsg.id = 'no-files-message';
                noFilesMsg.className = 'text-muted';
                noFilesMsg.textContent = 'No files listed. Add files or reload config.';
                container.appendChild(noFilesMsg);
            }
            // No need to re-sort after removal unless desired
        }
    }

     // --- NEW Event Handler ---
     function handleSaveFilesClick() {
        const saveBtn = document.getElementById('saveFilesBtn');
        const wdPath = document.getElementById('workingDirectoryInput').value;
        const container = document.getElementById('codeItems');

        if (!wdPath) {
            toastr.error("Working directory must be set to save files.", "Save Error");
            return;
        }

        // Collect current file paths from the list
        const currentFiles = Array.from(container.querySelectorAll('.code-item input[name="files"]'))
                                  .map(input => input.value);

        saveBtn.disabled = true;
        saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';

        fetch('/update_files', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json', // Sending JSON
            },
            body: JSON.stringify({ // Stringify the payload
                wd: wdPath,
                files: currentFiles
            })
        })
        .then(response => {
            if (!response.ok) {
                // Try to parse error JSON from backend
                 return response.json().then(errData => {
                    throw new Error(errData.error || `HTTP error ${response.status}`);
                }).catch(() => {
                     // If parsing JSON fails, throw generic error
                    throw new Error(`HTTP error ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                toastr.success(data.message || "File list saved successfully!", "Save Successful");
                setFileListDirty(false); // Mark as clean after successful save
            } else {
                 // Should be caught by !response.ok, but handle just in case
                toastr.error(data.error || "An unknown error occurred during save.", "Save Error");
                 saveBtn.disabled = false; // Re-enable on logical error from backend
            }
        })
        .catch(error => {
            console.error('Save Files Error:', error);
            toastr.error(error.message || "An error occurred while saving.", "Save Error");
            saveBtn.disabled = false; // Re-enable button on fetch/network error
        })
        .finally(() => {
            // Only reset button text if it wasn't set to clean (i.e., if an error occurred)
             if (saveBtn.disabled === false) {
                 saveBtn.innerHTML = '<i class="bi bi-save"></i> Save';
             }
        });
     }


    // --- Event Listeners Setup ---
    document.addEventListener('DOMContentLoaded', function () {

        // ... (keep existing initial setup for path shortening, sort, textarea resize) ...

        // --- MODIFIED/NEW Listeners ---

        // Reload Config button (ensure it resets dirty state)
        document.getElementById('reloadConfigBtn')?.addEventListener('click', function () {
            // ... (existing fetch logic inside) ...
            // Add this inside the .finally() block of the reload fetch:
            setFileListDirty(false); // Reset dirty state on reload
        });

        // Add File Button
        document.getElementById('addFileBtn')?.addEventListener('click', handleAddFileClick);

        // Allow adding file by pressing Enter in the input field
        document.getElementById('newFilePathInput')?.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault(); // Prevent potential form submission if it were in a form
                handleAddFileClick();
            }
        });

        // Save Files Button
        document.getElementById('saveFilesBtn')?.addEventListener('click', handleSaveFilesClick);

        // Remove File Buttons (using event delegation on the container)
        document.getElementById('codeItems')?.addEventListener('click', function(event) {
            if (event.target.closest('.remove-file-btn')) {
                handleRemoveFileClick(event);
            }
        });

        // Existing file list checkbox change listener (for sorting) - keep as is
        document.getElementById('codeItems')?.addEventListener('change', function (e) {
            if (e.target.matches('.form-check-input[name="files"]')) {
                sortFileList();
                // Note: Simply checking/unchecking doesn't make the list "dirty" for saving.
                // Only adding/removing does.
            }
        });


        // ... (keep other existing listeners: generate, gitDiffBtn, copyBtn, selectAll, clearAll, prompt links) ...

        // Initial state for save button
        setFileListDirty(false);

    }); // End DOMContentLoaded
</script>
```

**Explanation of Changes:**

2.  **Frontend (`index.html`):**
    *   **HTML:** Added the input field, add button, save button, and remove buttons per file. Structured the file item for better alignment. Added `id="codeItems"` container.
    *   **JavaScript:**
        *   `setFileListDirty`: Manages the enabled/disabled state of the "Save" button.
        *   `createFileListElement`: DRY helper function to generate the HTML for a file list item, including attaching the remove handler.
        *   `updateUIWithData`: Modified to clear only file items, use the `createFileListElement` helper, handle the "no files" message correctly, and call `setFileListDirty(false)` after loading.
        *   `handleAddFileClick`: Handles adding a new file path from the input, performs basic validation (empty, duplicate), updates the DOM, clears the input, sorts, and calls `setFileListDirty(true)`.
        *   `handleRemoveFileClick`: Handles removing a file item from the DOM when its remove button is clicked and calls `setFileListDirty(true)`. Adds back the "no files" message if needed.
        *   `handleSaveFilesClick`: Collects all current file paths from the DOM, gets the WD, sends the data via `fetch` (as JSON) to the new `/update_files` backend endpoint, handles success/error responses with toastr messages, and updates the save button state (`setFileListDirty(false)` on success).
        *   **Event Listeners:** Added listeners for the new Add, Save, and Remove buttons (using event delegation for Remove). The Reload listener now also resets the dirty state. Added a 'keypress' listener to the add input for Enter key.