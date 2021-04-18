/**
 * Initializes autocomplete dropdown for the elements provided in the input.
 * Code derived from W3Schools.
 *
 * @param inp Input Element to add the event listener to.
 * @param arr List of all input suggestions to possibly display in the dropdown.
 */
function initAutoCompleteDropdown(inp, arr) {
    let currentFocus;
    inp.addEventListener("input", (e) => {
        let inputDOM = e.target;
        let a, b, i, val = inputDOM.value;

        closeAllLists();
        if (!val) {
            return false;
        }
        currentFocus = -1;

        // Create div element of dropdown
        a = document.createElement("div");
        a.setAttribute("id", inputDOM.id + "autocomplete-list");
        a.setAttribute("class", "autocomplete-items");
        inputDOM.parentNode.appendChild(a);

        // TODO: Add a "No suggestions" option when there are no valid suggestions based on user's query.

        // Check similarity for each element in the suggestion list
        for (i = 0; i < arr.length; i++) {
            if (isSimilarEnough(val, arr[i])) {
                a.appendChild(createSuggestion(arr[i], inp)); // Append suggestion div to dropdown
            }
        }
        if (a.childElementCount == 0) {
            a.appendChild(createSuggestion("No artist found", inp, true));
        } else if (a.classList.includes('dummy_dropdown')) {
            // TODO(celine): Make dummy element unselectable
        }
    });

    // Lets users key up and down between suggestions
    inp.addEventListener("keydown", (keydownEvent) => {
        let x = document.getElementById(keydownEvent.target.id + "autocomplete-list");
        if (x) x = x.getElementsByTagName("div");
        if (keydownEvent.key == "Enter") {
            if (currentFocus > -1) {
                keydownEvent.preventDefault();
                if (x) x[currentFocus].click();
            }
        } else if (keydownEvent.key == "ArrowDown") {
            currentFocus++;
            addActive(x);
        } else if (keydownEvent.key == "ArrowUp") {
            currentFocus--;
            addActive(x);
        } else if (keydownEvent.key == 'Escape') {
            closeAllLists();
            currentFocus = -1;
        }
    });

    function addActive(x) {
        if (!x) return false;
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
        x[currentFocus].classList.add("autocomplete-active");
    }
    function removeActive(x) {
        for (let i = 0; i < x.length; i++) {
            x[i].classList.remove("autocomplete-active");
        }
    }
    function closeAllLists(elmnt) {
        let x = document.getElementsByClassName("autocomplete-items");
        for (let i = 0; i < x.length; i++) {
            if (elmnt != x[i] && elmnt != inp) {
                x[i].parentNode.removeChild(x[i]);
            }
        }
    }
    function createSuggestion(suggestionContent, inputDOM, opt_isUnselectable) {
        let suggestion = document.createElement("div");
        suggestion.innerHTML = suggestionContent;
        if (!opt_isUnselectable) {
            suggestion.setAttribute("class", "autocomplete-suggestion");
            suggestion.innerHTML += "<input type='hidden' value='" + suggestionContent + "'>";

            // Search field populates on suggestion click
            suggestion.addEventListener("click", (elClickEvent) => {
                inputDOM.value = elClickEvent.target.getElementsByTagName("input")[0].value;
                closeAllLists();
            });
        } else {
            suggestion.setAttribute("class", "autocomplete-suggestion autocomplete-dummy");
        }
        return suggestion;
    }
    function isDummyDropdown(inputDOM) {
        return false;
    }

    // Close dropdown when user clicks on a suggestion
    document.addEventListener("click", (clickEvent) => {
        closeAllLists(clickEvent.target);
    });
}

/**
 * Returns true if the two strings are similar enough for the target string to be suggested as an input.
 *
 * @param userInput {string} Name of artist that the user is expressing
 * @param targetString {string} Name of an artist in our known database
 * @returns {boolean} Whether it is worth suggesting targetString as an input.
 */
function isSimilarEnough(userInput, targetString) {
    // Right now we are just using substring equals.
    // TODO: Potentially implement some form of simple cosine sim...?
    return targetString.substr(0, userInput.length).toUpperCase() == userInput.toUpperCase();
}
