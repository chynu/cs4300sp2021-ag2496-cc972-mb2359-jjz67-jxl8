$('.spotify.followers').on("click", (e) => {
    console.log("HELLO!");
   let artistBody = $(e.target).parent().parent();
   let player = artistBody.find(".spotify-player");
   if (player.attr("data-active") == "true") {
       // Close player
       player.removeClass("expanded");
       player.attr("data-active", "false");
   } else {
       // Open player
       player.addClass("expanded");
       player.attr("data-active", "true");
   }
});