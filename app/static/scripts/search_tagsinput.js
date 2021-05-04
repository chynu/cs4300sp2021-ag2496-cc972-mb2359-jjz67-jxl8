$('input.tag').on('keydown', (e) => {
    if (e.key == "Enter" || e.key == ",") {
        e.preventDefault();
        let inputDOM = $(e.target);
        let dataId = inputDOM.attr('data-id');
        let val = inputDOM.val();
        let tagsDiv = inputDOM.parent().parent(); // ".tags_input" class

        // Create a tag element
        let newTag = createTag(val, dataId);
        let allCurrentTags = tagsDiv.find(".user-tag");
        if (allCurrentTags.length > 0) {
            let lastAddedTag = $(allCurrentTags[allCurrentTags.length - 1]);
            lastAddedTag.after(newTag);
        } else {
            tagsDiv.find(".tag-input-div").before(newTag);
        }

        inputDOM.val("");
    }
});

function createTag(content, dataId) {
    // Create DOM part of tag
    let newTag = $(document.createElement("div"));
    newTag.attr('data-id', dataId);
    newTag.attr('class', 'user-tag');
    newTag.html(content);

    // Add to hidden input
    let hiddenInputVal = $("#" + dataId).val();
    $("#" + dataId).val(hiddenInputVal + "," + content);

    // Add click listener so it disappears on click
    newTag.on("click", (e) => {
        let tags = $("#" + dataId).val().split(",");
        let i = tags.indexOf(content);
        if (i < 0) {
            console.warn("WARNING: Clicked tag cannot be found.");
        }
        tags.splice(i, 1);
        tags = tags.join(",");
        $("#" + dataId).val(tags);

        newTag.remove();
    });

    return newTag;
}

/**
 * Initializes autocomplete dropdown for the elements provided in the input.
 * Code derived from W3Schools.
 *
 * @param inp Input Element to add the event listener to.
 * @param arr List of all input suggestions to possibly display in the dropdown.
 */
function initializeTagsInput(inputElement, arr) {
    let currentFocus;

    // Whenever the user changes their input, we must
    // update/re-render the suggestion drop-down list.
    inputElement.on("input", (e) => {
        let inputDOM = $(e.target);
        let val = inputDOM.value;

        closeAllLists();
        if (!val) { return false; }
        currentFocus = -1;

        createAndFillDropdown(inputDOM);
    });

    // Listen for specific keystrokes to allow users to
    // navigate through the suggestion dropdown with their keyboard.
    inputElement.on("keydown", onUserKeyDown);

    /**
     * Creates a dropdown element that is populated with the suggestions corresponding to the user's
     * current input. This will be removed and re-rendered every time the user changes the input.
     * @param inputDOM
     */
    function createAndFillDropdown(inputDOM) {
        // Create div element of dropdown
        let autoDropdownDiv = document.createElement("div");
        let userInputValue = inputDOM.value;
        autoDropdownDiv.setAttribute("id", inputDOM.id + "autocomplete-list");
        autoDropdownDiv.setAttribute("class", "autocomplete-items");
        inputDOM.appendChild(autoDropdownDiv);

        // Check similarity for each element in the suggestion list
        for (let i = 0; i < arr.length; i++) {
            let suggestion = arr[i];
            if (isSimilarEnough(userInputValue, suggestion)) {
                a.appendChild(createSuggestion(suggestion, inputElement)); // Append suggestion div to dropdown
            }
        }
        if (a.childElementCount == 0) {
            a.appendChild(createSuggestion("No artist found", inputElement, true));
        } // TODO: Make dummy element unselectable
    }

    /**
     * Changes the highlighted or "active" element within the suggestion dropdown so that the user
     * can navigate between suggestions within the dropdown (so that they can ultimately choose
     * a suggestion by simply pressing the "enter" key).
     * @param keyDownEvent
     */
    function onUserKeyDown(keyDownEvent) {
        // THIS FUNCTION IS RUN EVERY TIME A USER PRESSES A KEY
        let activeSuggestionList = $("#" + keyDownEvent.target.id + "autocomplete-list");
        if (activeSuggestionList.length > 0) {
            activeSuggestionList = activeSuggestionList.find("div");
        }

        if (keyDownEvent.key == "Enter") {
            if (currentFocus > -1) {
                keydownEvent.preventDefault();
                if (x) x[currentFocus].click();
            }
        } else if (keyDownEvent.key == "ArrowDown") {
            currentFocus++;
            addActive(x);
        } else if (keyDownEvent.key == "ArrowUp") {
            currentFocus--;
            addActive(x);
        } else if (keyDownEvent.key == 'Escape') {
            closeAllLists();
            currentFocus = -1;
        }
    }

    /**
     * Helper function for marking a given suggestion as highlighted/"active".
     * @param x
     * @returns {boolean}
     */
    function addActive(x) {
        if (!x) return false;
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
        x[currentFocus].classList.add("autocomplete-active");
    }

    /**
     * Helper function for removing the "active" marking.
     * @param x
     */
    function removeActive(x) {
        for (let i = 0; i < x.length; i++) {
            x[i].classList.remove("autocomplete-active");
        }
    }

    /**
     * Helper function for closing the entire suggestion list and removing it from the DOM.
     * Optionally takes in an element which is used to populate the actual input element
     * to be passed to the back-end.
     * @param elmnt
     */
    function closeAllLists(elmnt) {
        let x = document.getElementsByClassName("autocomplete-items");
        for (let i = 0; i < x.length; i++) {
            if (elmnt != x[i] && elmnt != inp) {
                x[i].parentNode.removeChild(x[i]);
            }
        }
    }

    /**
     * Creates a DOM element for a single dropdown option within the suggestions list.
     * @param suggestionContent
     * @param inputDOM
     * @param opt_isUnselectable
     * @returns {HTMLDivElement}
     */
    function createSuggestion(suggestionContent, inputDOM, opt_isUnselectable) {
        let suggestion = document.createElement("div");
        suggestion.innerHTML = suggestionContent;
        if (!opt_isUnselectable) {
            suggestion.setAttribute("class", "autocomplete-suggestion");
            suggestion.innerHTML += "<input type='hidden' value='" + suggestionContent + "'>";

            // Search field populates on suggestion click
            suggestion.addEventListener("click", (elClickEvent) => {
                let inp_id = $(inputDOM).attr('data-id');
                console.log("data-id:", inp_id);

                let inp_ = $('input#' + inp_id);
                inp_.val(elClickEvent.target.getElementsByTagName("input")[0].value);
                console.log(inp_, inp_.val());

                // inputDOM.value = elClickEvent.target.getElementsByTagName("input")[0].value;
                closeAllLists();
            });
        } else {
            suggestion.setAttribute("class", "autocomplete-suggestion autocomplete-dummy");
        }
        return suggestion;
    }

    // Close dropdown when user clicks on a suggestion
    document.addEventListener("click", (clickEvent) => {
        closeAllLists(clickEvent.target);
    });
}

