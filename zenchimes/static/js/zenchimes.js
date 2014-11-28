var ZenChimes = {
    init: function () {
        // data
        ZenChimes.chimes = new ChimesList();
        ZenChimes.chimes.fetch({reset: true});
        ZenChimes.playList = [];
        ZenChimes.play = {};

        // views
        ZenChimes.chimesList = new ChimesView({collection: ZenChimes.chimes});

        ZenChimes.chimesList.render();
    }
}

$(function(){
    ZenChimes.init();
});

// Chime Model
// -----------
// Basic Chime model has `is_active` and `description` attributes.
var Chime = Backbone.Model.extend({

    // Default attributes ensure that each chime created has `description`
    // and `is_active` keys.
    defaults: function() {
        return {
            description: '',
            filename: '',
            is_active: false
        };
    },

    // Toggle the `is_active` state of the item. The REST API call will
    // set this one active and all others inactive.
    toggle: function() {
        console.log('In model.Chime.toggle');
        this.save({
            is_active: !this.get('is_active'),
        });
    }
});


// Chimes Collection
// -----------------

var ChimesList = Backbone.Collection.extend({
    // Reference to this collection's model.
    model: Chime,
    url: '/chimes',
});

var ChimesView = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, "render", "addOne", "addAll");
        this.collection.bind("reset", this.render);
    },

    tagName: "ul",
    className: "list-unstyled",

    render: function() {
        //this.$el.html(this.template);
        this.addAll();
        this.$el.html(ZenChimes.chimeItems);
        $("#chimeapp").append(this.el);
        return this;
    },

    addAll: function() {
        ZenChimes.chimeItems = [];
        this.collection.each(this.addOne);
    },

    addOne: function(model) {
        var view = new ChimeView({ id: model.get('id'), model: model });
        var chime_item = view.render();
        ZenChimes.chimeItems.push(chime_item.el);
    }
});

// ChimeView - Individual item view
// --------------------------------
var ChimeView = Backbone.View.extend({
    tagName: "li",

    events: {
        "click .toggle": "toggleActive",
        "click .playbutton": "playHandler"
    },

    render: function() {
        template = $("#chime-template").html();
        compiled = _.template(template)(this.model.toJSON());
        this.$el.html(compiled);
        return this;
    },

    // Toggle chime selector for UI and model.
    toggleActive: function () {
        console.log("toggleActive click event");
        chime_id = this.model.get('id');

        // Since the previous selected id is not available, we need to
        // make one pass to turn them all off. Same as the REST API
        // against the DB.
        $(".chimeRad").each(function(i, obj) {
            if (obj.classList.contains('glyphicon-ok')) {
                obj.classList.remove('glyphicon-ok');
                obj.classList.add('glyphicon-unchecked');
            }
        });

        // Now  turn on selected.
        button_id = '#chimeRadio-' + chime_id;
        selected_obj = $(button_id)[0];
        selected_obj.classList.remove('glyphicon-unchecked');
        selected_obj.classList.add('glyphicon-ok');

        // Toggle the model.
        this.model.toggle();
    },
    playHandler: function () {
        // Play/pause button click handler.
        // --------------------------------
        play_button_id = "playButton-" + this.model.get("id");
        ZenChimes.playList[ play_button_id ] = this.model.get("filename");
        var el = $("#" + play_button_id)[0];

        if (ZenChimes.play instanceof Audio) {
            if ((ZenChimes.play.el_id == play_button_id) && ZenChimes.play.paused) {
                ZenChimes.play.play()
                el.classList.remove('glyphicon-play');
                el.classList.add('glyphicon-pause');
                return;
            } else if ((ZenChimes.play.el_id == play_button_id) && !ZenChimes.play.paused) {
                el.classList.remove('glyphicon-pause');
                el.classList.add('glyphicon-play');
                ZenChimes.play.pause();
                return;
            } else {
                var button_el = $("#" + ZenChimes.play.el_id)[0];
                button_el.classList.remove('glyphicon-pause');
                button_el.classList.add('glyphicon-play');
                ZenChimes.play.pause();
            }
        }

        ZenChimes.play = new Audio('/mp3/' + ZenChimes.playList[play_button_id]);
        ZenChimes.play.el_id = play_button_id;

        el.classList.remove('glyphicon-play');
        el.classList.add('glyphicon-pause');

        ZenChimes.play.addEventListener('ended', function() {
            var button_el = $("#" + ZenChimes.play.el_id)[0];
            button_el.classList.remove('glyphicon-pause');
            button_el.classList.add('glyphicon-play');
            ZenChimes.play = null;
        });

        ZenChimes.play.play();
    },
});

