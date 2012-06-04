var app = (function ($){
	var Router = Backbone.Router.extend({
        el: null,
        initialize: function(el) {
            this.el = el;

            this.mainView = new MainView();
        },
		routes: {
            "": "main",
            "contact": "contact",
        },
        main: function() {
            this.mainView = new MainView();
            this.mainView.render();
        },
        contact: function() {
            this.contactView = new ContactView();
            this.contactView.render();
        },
	});

    var MainView = Backbone.View.extend({
        tmplHtml: $('#main-tmpl').html(),
        template: null,
        el: $('#content'),
        initialize: function(){
            this.template = Handlebars.compile(this.tmplHtml);
        },
        render: function(){
            html = this.template();
            $(this.el).html(html);
        },
    });

    var CreoleView = Backbone.View.extend({
        el: null,
        creole: null,
        options: {},
        initialize: function(){
            this.creole = new Parse.Simple.Creole({
                forIE: document.all,
            });
        },
        render: function(div, markup){
                this.creole.parse(div, markup);
        },
    });

    var ContactView = Backbone.View.extend({
        creoleView: null,
        tmplHtml: $('#contact-tmpl').html(),
        el: $('#content'),
        initialize: function(){
            this.template = Handlebars.compile(this.tmplHtml);
            this.creoleView = new CreoleView();
        },
        render: function(){
            var context = {};
            html = this.template(context);
            $(this.el).html(html);
        },
    });

    $(document).ready(function(){
        var content = $('#content');
        var app = new Router(content);
        Backbone.history.start();
    });

    return app;
})(jQuery);
