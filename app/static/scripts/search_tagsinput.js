const MORE_ARTISTS_MSG = "add more...";
const DISLIKED_ARTIST_MSG = "artists you don't like";
const LIKED_ARTIST_MSG = "your favorite artist";

$('input.tag').on('keydown', (e) => {
    let inputDOM = $(e.target);
    if (e.key == "Enter") {
        // Handling for the case in which the user enters an invalid query.
        // let hiddenInput = $("#" + inputDOM.attr("data-id"));
        // hiddenInput.val(inputDOM.val());
    }
    if (e.key == "Backspace" & $(e.target).val() == "") {
        e.preventDefault();
        let tagsDiv = inputDOM.parent().parent(); // ".tags_input" class
        let allCurrentTags = tagsDiv.find(".user-tag");
        let lastAddedTag = $(allCurrentTags[allCurrentTags.length - 1]);
        removeTag(lastAddedTag);
    }
});

function turnToTag(inputDOM, opt_val) {
    let dataId = inputDOM.attr('data-id');
    let val = !opt_val ? inputDOM.val() : opt_val;
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
    inputDOM.attr("placeholder", MORE_ARTISTS_MSG);
}

function injectTag(content, inputId) {
    turnToTag($("#" + inputId), content)
}

function createTag(content, dataId) {
    // Create DOM part of tag
    let newTag = $(document.createElement("div"));
    newTag.attr('data-id', dataId);
    newTag.attr('class', 'user-tag');
    newTag.html(content);

    // Add to hidden input
    let hiddenInputVal = $("#" + dataId).val();
    if (hiddenInputVal.length > 0) {
        $("#" + dataId).val(hiddenInputVal + "," + content);
    } else {
        $("#" + dataId).val(content);
    }

    // Add click listener so it disappears on click
    newTag.on("click", (e) => {
        removeTag(newTag);
    });

    return newTag;
}

function removeTag(tagObj) {
    let dataId = tagObj.attr('data-id');
    let content = tagObj.html();
    let tags = $("#" + dataId).val().split(",");

    // Remove tag from the actual record of tags
    let i = tags.indexOf(content);
    if (i < 0) {
        console.warn("WARNING: Clicked tag cannot be found.");
    }
    tags.splice(i, 1);
    tags = tags.join(",");
    $("#" + dataId).val(tags);

    if (tags.length == 0) {
        let tagInputDOM = $(tagObj.parent().find(".tag-input-div").find("input.tag")[0]);
        if (tagInputDOM.hasClass("disliked_artist")) {
            tagInputDOM.attr("placeholder", DISLIKED_ARTIST_MSG);
        } else if (tagInputDOM.hasClass("fav_artist")) {
            tagInputDOM.attr("placeholder", LIKED_ARTIST_MSG);
        }

    }

    tagObj.remove();
}

