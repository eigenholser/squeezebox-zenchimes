var Chime = null;
var ChimesList = null;
var ChimesView = null;
var ChimeView = null;
var chimes = null;
var play = {};
var playlist = new Array();

$(function(){

    // Play the selected chime
    // -----------------------
    $(".glyphicon-play").click(function() {
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

    ChimesList = Backbone.Collection.extend({
        // Reference to this collection's model.
        model: Chime,
        url: '/chimes',

        initialize: function() {
            console.log("Chimes collection initialize");
        }
    });

    ChimesView = Backbone.View.extend({
        el: $("#chimeapp"),

        template: _.template( $('#chimes-template').html() ),

        initialize: function() {
            console.log("ChimesView initialize");
            _.bindAll(this, "render", "addOne", "addAll");
            this.collection.bind("reset", this.render);
        },

        render: function() {
            console.log("render");
            console.log(this.collection.length);
            $(this.el).html(this.template());
            this.addAll();
        },

        addAll: function() {
            console.log("addAll");
            this.collection.each(this.addOne);
        },

        addOne: function(model) {
            console.log("addOne");
            view = new ChimeView({ model: model });
            $("ul", this.el).append(view.render());

            play_button_id = "playButton-" + model.get("id");
            playlist[ play_button_id ] = model.get("filename");

            // Play/pause button click handler.
            // --------------------------------
            $("#" + play_button_id).click(function() {
                if (play instanceof Audio) {
                    console.log("play is instance of Audio");

                    if ((play.el_id == this.id) && play.paused) {
                        console.log("resume");
                        play.play()
                        this.classList.remove('glyphicon-play');
                        this.classList.add('glyphicon-pause');
                        return;
                    } else if ((play.el_id == this.id) && !play.paused) {
                        console.log("same pause");
                        this.classList.remove('glyphicon-pause');
                        this.classList.add('glyphicon-play');
                        play.pause();
                        return;
                    } else {
                        console.log("pause");
                        var button_el = $("#" + play.el_id)[0];
                        button_el.classList.remove('glyphicon-pause');
                        button_el.classList.add('glyphicon-play');
                        play.pause();
                        //play = null;
                    }
                }

                console.log('/mp3/' + playlist[ this.id ]);

                play = new Audio('/mp3/' + playlist[ this.id ]);
                play.el_id = this.id;

                this.classList.remove('glyphicon-play');
                this.classList.add('glyphicon-pause');

                play.addEventListener('ended', function() {
                    console.log("ended handler");
                    var button_el = $("#" + play.el_id)[0];
                    button_el.classList.remove('glyphicon-pause');
                    button_el.classList.add('glyphicon-play');
                    play = null;
                });

                play.play();
            });
        }
    });

    // ChimeView - Individual item view
    // --------------------------------
    ChimeView = Backbone.View.extend({
        tagName: "li",
        template: _.template( $('#chime-template').html() ),

        events: {
            "click .toggle": "toggleActive"
        },

        initialize: function() {
            _.bindAll(this, "render");

            // Bootstrap needs to know
            status = this.model.get('is_active') ? "active" : "";
            // this.$el.attr( "class", "list-group-item " + status );
        },

        render: function() {
            return $(this.el).append(this.template(this.model.toJSON()));
        },

        // Toggle chime selector for UI and model.
        toggleActive: function() {
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
        }
    });

    // Router
    // ------
    Router = Backbone.Router.extend({
        routes: {
            "": "defaultRoute" // http://localhost:8000
        },

        defaultRoute: function() {
            console.log("defaultRoute");
            chimes = new ChimesList();
            new ChimesView({ collection: chimes });
            chimes.fetch({reset:true});
            console.log(chimes.length);
        }
    });

    var appRouter = new Router();
    Backbone.history.start();
});
