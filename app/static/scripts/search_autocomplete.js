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
                // If similar enough, display in dropdown
                b = document.createElement("div");
                b.setAttribute("class", "autocomplete-suggestion");
                b.innerHTML = arr[i];
                b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";

                // Search field populates on suggestion click
                b.addEventListener("click", (elClickEvent) => {
                    inp.value = elClickEvent.target.getElementsByTagName("input")[0].value;
                    closeAllLists();
                });

                // Append suggestion div to dropdown
                a.appendChild(b);
            }
        }
    });

    // Lets users key up and down between suggestions
    inp.addEventListener("keydown", (keydownEvent) => {
        let x = document.getElementById(keydownEvent.target.id + "autocomplete-list");
        if (x) x = x.getElementsByTagName("div");
        if (keydownEvent.key == "Enter") {
            keydownEvent.preventDefault();
            if (currentFocus > -1) {
                if (x) x[currentFocus].click();
            }
        } else if (keydownEvent.key == "ArrowDown") {
            currentFocus++;
            addActive(x);
        } else if (keydownEvent.key == "ArrowUp") {
            currentFocus--;
            addActive(x);
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

let countries = ["Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua & Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bermuda", "Bhutan", "Bolivia", "Bosnia & Herzegovina", "Botswana", "Brazil", "British Virgin Islands", "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cambodia", "Cameroon", "Canada", "Cape Verde", "Cayman Islands", "Central Arfrican Republic", "Chad", "Chile", "China", "Colombia", "Congo", "Cook Islands", "Costa Rica", "Cote D Ivoire", "Croatia", "Cuba", "Curacao", "Cyprus", "Czech Republic", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Ethiopia", "Falkland Islands", "Faroe Islands", "Fiji", "Finland", "France", "French Polynesia", "French West Indies", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Gibraltar", "Greece", "Greenland", "Grenada", "Guam", "Guatemala", "Guernsey", "Guinea", "Guinea Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Isle of Man", "Israel", "Italy", "Jamaica", "Japan", "Jersey", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Kosovo", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Macau", "Macedonia", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauro", "Nepal", "Netherlands", "Netherlands Antilles", "New Caledonia", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Korea", "Norway", "Oman", "Pakistan", "Palau", "Palestine", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Reunion", "Romania", "Russia", "Rwanda", "Saint Pierre & Miquelon", "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Korea", "South Sudan", "Spain", "Sri Lanka", "St Kitts & Nevis", "St Lucia", "St Vincent", "Sudan", "Suriname", "Swaziland", "Sweden", "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Timor L'Este", "Togo", "Tonga", "Trinidad & Tobago", "Tunisia", "Turkey", "Turkmenistan", "Turks & Caicos", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States of America", "Uruguay", "Uzbekistan", "Vanuatu", "Vatican City", "Venezuela", "Vietnam", "Virgin Islands (US)", "Yemen", "Zambia", "Zimbabwe"];
let artists = ["Beyonce", "Beatrice", "Rihanna", "Ricch Roddy"];

initAutoCompleteDropdown(document.getElementsByClassName("fav_artist")[0], artists);
initAutoCompleteDropdown(document.getElementsByClassName("disliked_artist")[0], artists);
