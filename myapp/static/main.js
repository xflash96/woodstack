var app = (function ($){
	var main = Backbone.Router.extend({
		routes: {
            "post": "listPost",
            "post/*post": "viewPost",
            "*page": "defaultAction",
        },
        defaultAction: function( page ){
            $.ajax({
                url: "",
                dataType: "jsonp",
                success: function(data){
                }
            })
        }
	});

    var mainView = Backbone.View.extend({
        template: "",
        el: $('#main'),
        events: {
        },
        initialize: function(){
            this.model.bind('change', this.render, this);
            this.model.bind('destroy', this.remove, this);
        },
        render: function(){
        },
        destroy: function(){
        },
    });

    var app = new main;
    Backbone.history.start();

    return app;
})(jQuery);
