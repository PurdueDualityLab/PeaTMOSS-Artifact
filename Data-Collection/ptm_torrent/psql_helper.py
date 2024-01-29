import psycopg2


def init_db(cursor):

    cursor.execute("DROP TABLE IF EXISTS public.model CASCADE")
    cursor.execute("CREATE TABLE public.model ( \
        id serial NOT NULL, \
        model_hub integer NOT NULL, \
        context_id TEXT NOT NULL, \
        repo_url TEXT NOT NULL, \
        CONSTRAINT model_p PRIMARY KEY (id) \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.model_hub CASCADE")
    cursor.execute("CREATE TABLE public.model_hub ( \
        model_hub_id serial NOT NULL, \
        url TEXT NOT NULL, \
        name TEXT NOT NULL, \
        CONSTRAINT model_hub_pk PRIMARY KEY (model_hub_id) \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.model_to_tag CASCADE")
    cursor.execute("CREATE TABLE public.model_to_tag ( \
        model_id integer NOT NULL, \
        tag_id integer NOT NULL \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.tag CASCADE")
    cursor.execute("CREATE TABLE public.tag ( \
        tag_id serial NOT NULL, \
        name TEXT NOT NULL, \
        CONSTRAINT tag_pk PRIMARY KEY (tag_id) \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.framework CASCADE")
    cursor.execute("CREATE TABLE public.framework ( \
        framework_id serial NOT NULL, \
        name TEXT NOT NULL, \
        CONSTRAINT framework_pk PRIMARY KEY (framework_id) \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.architecture CASCADE")
    cursor.execute("CREATE TABLE public.architecture ( \
        architecture_id serial NOT NULL, \
        name TEXT NOT NULL, \
        CONSTRAINT architecture_pk PRIMARY KEY (architecture_id) \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.model_hub_to_tag CASCADE")
    cursor.execute("CREATE TABLE public.model_hub_to_tag ( \
        model_hub_id integer NOT NULL, \
        tag_id integer NOT NULL \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.dataset CASCADE")
    cursor.execute("CREATE TABLE public.dataset ( \
        id serial NOT NULL, \
        model_hub integer NOT NULL, \
        context_id integer NOT NULL, \
        description TEXT NOT NULL, \
        CONSTRAINT dataset_pk PRIMARY KEY (id) \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.dataset_to_tag CASCADE")
    cursor.execute("CREATE TABLE public.dataset_to_tag ( \
        dataset_id integer NOT NULL, \
        tag_id integer NOT NULL \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.model_to_language CASCADE")
    cursor.execute("CREATE TABLE public.model_to_language ( \
        model_id integer NOT NULL, \
        language_id integer NOT NULL \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.language CASCADE")
    cursor.execute("CREATE TABLE public.language ( \
        language_id serial NOT NULL, \
        abbreviateion TEXT NOT NULL, \
        name TEXT NOT NULL, \
        CONSTRAINT language_pk PRIMARY KEY (language_id) \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.dataset_to_language CASCADE")
    cursor.execute("CREATE TABLE public.dataset_to_language ( \
        dataset_id integer NOT NULL, \
        language_id integer NOT NULL \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.model_to_framework CASCADE")
    cursor.execute("CREATE TABLE public.model_to_framework ( \
        model_id integer NOT NULL, \
        framework_id integer NOT NULL \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.model_to_architecture CASCADE")
    cursor.execute("CREATE TABLE public.model_to_architecture ( \
        model_id integer NOT NULL, \
        architecture_id integer NOT NULL \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.model_to_config_file CASCADE")
    cursor.execute("CREATE TABLE public.model_to_config_file ( \
        model_id integer NOT NULL, \
        config_file_id integer NOT NULL \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.config_file CASCADE")
    cursor.execute("CREATE TABLE public.config_file ( \
        config_file_id serial NOT NULL, \
        name TEXT NOT NULL, \
        file jsonb NOT NULL, \
        CONSTRAINT config_file_pk PRIMARY KEY (config_file_id) \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.model_to_author CASCADE")
    cursor.execute("CREATE TABLE public.model_to_author ( \
        model_id integer NOT NULL, \
        author_id integer NOT NULL \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.author CASCADE")
    cursor.execute("CREATE TABLE public.author ( \
        author_id serial NOT NULL, \
        name TEXT NOT NULL, \
        CONSTRAINT author_pk PRIMARY KEY (author_id) \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.model_to_library CASCADE")
    cursor.execute("CREATE TABLE public.model_to_library ( \
        model_id integer NOT NULL, \
        library_id integer NOT NULL \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.library CASCADE")
    cursor.execute("CREATE TABLE public.library ( \
        library_id serial NOT NULL, \
        name TEXT NOT NULL, \
        CONSTRAINT library_pk PRIMARY KEY (library_id) \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.model_to_paper CASCADE")
    cursor.execute("CREATE TABLE public.model_to_paper ( \
        model_id integer NOT NULL, \
        paper_id integer NOT NULL \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.paper CASCADE")
    cursor.execute("CREATE TABLE public.paper ( \
        paper_id serial NOT NULL, \
        url TEXT NOT NULL, \
        CONSTRAINT paper_pk PRIMARY KEY (paper_id) \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.dataset_to_paper CASCADE")
    cursor.execute("CREATE TABLE public.dataset_to_paper ( \
        datset_id integer NOT NULL, \
        paper_id integer NOT NULL \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.model_to_dataset CASCADE")
    cursor.execute("CREATE TABLE public.model_to_dataset ( \
        dataset_id integer NOT NULL, \
        model_id integer NOT NULL \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.model_to_license CASCADE")
    cursor.execute("CREATE TABLE public.model_to_license ( \
        model_id integer NOT NULL, \
        license_id integer NOT NULL \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.license CASCADE")
    cursor.execute("CREATE TABLE public.license ( \
        license_id serial NOT NULL, \
        name TEXT NOT NULL, \
        CONSTRAINT license_pk PRIMARY KEY (license_id) \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.dataset_to_license CASCADE")
    cursor.execute("CREATE TABLE public.dataset_to_license ( \
        dataset_id integer NOT NULL, \
        license_id integer NOT NULL \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.dataset_info CASCADE")
    cursor.execute("CREATE TABLE public.dataset_info ( \
        info_id serial NOT NULL, \
        file jsonb NOT NULL, \
        CONSTRAINT dataset_info_pk PRIMARY KEY (info_id) \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.dataset_to_info CASCADE")
    cursor.execute("CREATE TABLE public.dataset_to_info ( \
        dataset_id integer NOT NULL, \
        info_id integer NOT NULL \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.dataset_to_author CASCADE")
    cursor.execute("CREATE TABLE public.dataset_to_author ( \
        dataset_id integer NOT NULL, \
        author_id integer NOT NULL \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.model_to_representation CASCADE")
    cursor.execute("CREATE TABLE public.model_to_representation ( \
        model_id integer NOT NULL, \
        representation_id integer NOT NULL \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("DROP TABLE IF EXISTS public.representation CASCADE")
    cursor.execute("CREATE TABLE public.representation ( \
        representation_id serial NOT NULL, \
        name TEXT NOT NULL, \
        CONSTRAINT representation_pk PRIMARY KEY (representation_id) \
        ) WITH ( \
        OIDS=FALSE \
        );")
    
    cursor.execute("DROP TABLE IF EXISTS public.usage CASCADE")
    cursor.execute("CREATE TABLE public.usage ( \
        usage_id serial NOT NULL, \
        occurences integer NOT NULL, \
        model_id integer NOT NULL, \
        CONSTRAINT usage_pk PRIMARY KEY (usage_id) \
        ) WITH ( \
        OIDS=FALSE \
        );")
    
    cursor.execute("DROP TABLE IF EXISTS public.reuse_repository CASCADE")
    cursor.execute("CREATE TABLE public.reuse_repository ( \
        id serial NOT NULL, \
        github_url text NOT NULL, \
        CONSTRAINT reuse_repository_pk PRIMARY KEY (id) \
        ) WITH ( \
        OIDS=FALSE \
        );")
    
    cursor.execute("DROP TABLE IF EXISTS public.model_to_reuse CASCADE")
    cursor.execute("CREATE TABLE public.model_to_reuse ( \
        model_id integer NOT NULL, \
        reuse_id integer NOT NULL \
        ) WITH ( \
        OIDS=FALSE \
        );")
    
    cursor.execute("DROP TABLE IF EXISTS public.issues CASCADE")
    cursor.execute("CREATE TABLE public.issues ( \
        id serial NOT NULL, \
        issue jsonb NOT NULL, \
        CONSTRAINT issues_pk PRIMARY KEY (id) \
        ) WITH ( \
        OIDS=FALSE \
        );")
    
    cursor.execute("DROP TABLE IF EXISTS public.reuse_to_issues CASCADE")
    cursor.execute("CREATE TABLE public.reuse_to_issues ( \
        reuse_id integer NOT NULL, \
        issue_id integer NOT NULL \
        ) WITH ( \
        OIDS=FALSE \
        );")
    
    cursor.execute("DROP TABLE IF EXISTS public.reuse_to_prs CASCADE")
    cursor.execute("CREATE TABLE public.reuse_to_prs ( \
        reuse_id integer NOT NULL, \
        pr_id integer NOT NULL \
        ) WITH ( \
        OIDS=FALSE \
        );")
    
    cursor.execute("DROP TABLE IF EXISTS public.pull_requests CASCADE")
    cursor.execute("CREATE TABLE public.pull_requests ( \
        pr_id serial NOT NULL, \
        pull_request jsonb NOT NULL, \
        CONSTRAINT pull_requests_pk PRIMARY KEY (pr_id) \
        ) WITH ( \
        OIDS=FALSE \
        );")

    cursor.execute("ALTER TABLE model ADD CONSTRAINT model_fk0 FOREIGN KEY (model_hub) REFERENCES model_hub(model_hub_id);")

    cursor.execute("ALTER TABLE model_to_tag ADD CONSTRAINT model_to_tag_fk0 FOREIGN KEY (model_id) REFERENCES model(id);")

    cursor.execute("ALTER TABLE model_to_tag ADD CONSTRAINT model_to_tag_fk1 FOREIGN KEY (tag_id) REFERENCES tag(tag_id);")

    cursor.execute("ALTER TABLE model_hub_to_tag ADD CONSTRAINT model_hub_to_tag_fk0 FOREIGN KEY (model_hub_id) REFERENCES model_hub(model_hub_id);")

    cursor.execute("ALTER TABLE model_hub_to_tag ADD CONSTRAINT model_hub_to_tag_fk1 FOREIGN KEY (tag_id) REFERENCES tag(tag_id);")

    cursor.execute("ALTER TABLE dataset ADD CONSTRAINT dataset_fk0 FOREIGN KEY (model_hub) REFERENCES model_hub(model_hub_id);")

    cursor.execute("ALTER TABLE dataset_to_tag ADD CONSTRAINT dataset_to_tag_fk0 FOREIGN KEY (dataset_id) REFERENCES dataset(id);")

    cursor.execute("ALTER TABLE dataset_to_tag ADD CONSTRAINT dataset_to_tag_fk1 FOREIGN KEY (tag_id) REFERENCES tag(tag_id);")

    cursor.execute("ALTER TABLE model_to_language ADD CONSTRAINT model_to_language_fk0 FOREIGN KEY (model_id) REFERENCES model(id);")

    cursor.execute("ALTER TABLE model_to_language ADD CONSTRAINT model_to_language_fk1 FOREIGN KEY (language_id) REFERENCES language(language_id);")

    cursor.execute("ALTER TABLE dataset_to_language ADD CONSTRAINT dataset_to_language_fk0 FOREIGN KEY (dataset_id) REFERENCES dataset(id);")

    cursor.execute("ALTER TABLE dataset_to_language ADD CONSTRAINT dataset_to_language_fk1 FOREIGN KEY (language_id) REFERENCES language(language_id);")

    cursor.execute("ALTER TABLE model_to_framework ADD CONSTRAINT model_to_framework_fk0 FOREIGN KEY (model_id) REFERENCES model(id);")

    cursor.execute("ALTER TABLE model_to_framework ADD CONSTRAINT model_to_framework_fk1 FOREIGN KEY (framework_id) REFERENCES framework(framework_id);")

    cursor.execute("ALTER TABLE model_to_architecture ADD CONSTRAINT model_to_architecture_fk0 FOREIGN KEY (model_id) REFERENCES model(id);")

    cursor.execute("ALTER TABLE model_to_architecture ADD CONSTRAINT model_to_architecture_fk1 FOREIGN KEY (architecture_id) REFERENCES architecture(architecture_id);")

    cursor.execute("ALTER TABLE model_to_config_file ADD CONSTRAINT model_to_config_file_fk0 FOREIGN KEY (model_id) REFERENCES model(id);")

    cursor.execute("ALTER TABLE model_to_config_file ADD CONSTRAINT model_to_config_file_fk1 FOREIGN KEY (config_file_id) REFERENCES config_file(config_file_id);")

    cursor.execute("ALTER TABLE model_to_author ADD CONSTRAINT model_to_author_fk0 FOREIGN KEY (model_id) REFERENCES model(id);")

    cursor.execute("ALTER TABLE model_to_author ADD CONSTRAINT model_to_author_fk1 FOREIGN KEY (author_id) REFERENCES author(author_id);")

    cursor.execute("ALTER TABLE model_to_library ADD CONSTRAINT model_to_library_fk0 FOREIGN KEY (model_id) REFERENCES model(id);")

    cursor.execute("ALTER TABLE model_to_library ADD CONSTRAINT model_to_library_fk1 FOREIGN KEY (library_id) REFERENCES library(library_id);")

    cursor.execute("ALTER TABLE model_to_paper ADD CONSTRAINT model_to_paper_fk0 FOREIGN KEY (model_id) REFERENCES model(id);")

    cursor.execute("ALTER TABLE model_to_paper ADD CONSTRAINT model_to_paper_fk1 FOREIGN KEY (paper_id) REFERENCES paper(paper_id);")

    cursor.execute("ALTER TABLE dataset_to_paper ADD CONSTRAINT dataset_to_paper_fk0 FOREIGN KEY (datset_id) REFERENCES dataset(id);")

    cursor.execute("ALTER TABLE dataset_to_paper ADD CONSTRAINT dataset_to_paper_fk1 FOREIGN KEY (paper_id) REFERENCES paper(paper_id);")

    cursor.execute("ALTER TABLE model_to_dataset ADD CONSTRAINT model_to_dataset_fk0 FOREIGN KEY (dataset_id) REFERENCES dataset(id);")

    cursor.execute("ALTER TABLE model_to_dataset ADD CONSTRAINT model_to_dataset_fk1 FOREIGN KEY (model_id) REFERENCES model(id);")

    cursor.execute("ALTER TABLE model_to_license ADD CONSTRAINT model_to_license_fk0 FOREIGN KEY (model_id) REFERENCES model(id);")

    cursor.execute("ALTER TABLE model_to_license ADD CONSTRAINT model_to_license_fk1 FOREIGN KEY (license_id) REFERENCES license(license_id);")

    cursor.execute("ALTER TABLE dataset_to_license ADD CONSTRAINT dataset_to_license_fk0 FOREIGN KEY (dataset_id) REFERENCES dataset(id);")

    cursor.execute("ALTER TABLE dataset_to_license ADD CONSTRAINT dataset_to_license_fk1 FOREIGN KEY (license_id) REFERENCES license(license_id);")

    cursor.execute("ALTER TABLE dataset_to_info ADD CONSTRAINT dataset_to_info_fk0 FOREIGN KEY (dataset_id) REFERENCES dataset(id);")

    cursor.execute("ALTER TABLE dataset_to_info ADD CONSTRAINT dataset_to_info_fk1 FOREIGN KEY (info_id) REFERENCES dataset_info(info_id);")

    cursor.execute("ALTER TABLE dataset_to_author ADD CONSTRAINT dataset_to_author_fk0 FOREIGN KEY (dataset_id) REFERENCES dataset(id);")

    cursor.execute("ALTER TABLE dataset_to_author ADD CONSTRAINT dataset_to_author_fk1 FOREIGN KEY (author_id) REFERENCES author(author_id);")

    cursor.execute("ALTER TABLE model_to_representation ADD CONSTRAINT model_to_representation_fk0 FOREIGN KEY (model_id) REFERENCES model(id);")

    cursor.execute("ALTER TABLE model_to_representation ADD CONSTRAINT model_to_representation_fk1 FOREIGN KEY (representation_id) REFERENCES representation(representation_id);")

    cursor.execute("ALTER TABLE usage ADD CONSTRAINT usage_fk0 FOREIGN KEY (model_id) REFERENCES model(id);")

    cursor.execute("ALTER TABLE model_to_reuse ADD CONSTRAINT model_to_reuse_fk0 FOREIGN KEY (model_id) REFERENCES model(id);")

    cursor.execute("ALTER TABLE model_to_reuse ADD CONSTRAINT model_to_reuse_fk1 FOREIGN KEY (reuse_id) REFERENCES reuse_repository(id);")

    cursor.execute("ALTER TABLE reuse_to_issues ADD CONSTRAINT reuse_to_issues_fk0 FOREIGN KEY (reuse_id) REFERENCES reuse_repository(id);")

    cursor.execute("ALTER TABLE reuse_to_issues ADD CONSTRAINT reuse_to_issues_fk1 FOREIGN KEY (issue_id) REFERENCES issues(id);")

    cursor.execute("ALTER TABLE reuse_to_prs ADD CONSTRAINT reuse_to_prs_fk0 FOREIGN KEY (reuse_id) REFERENCES reuse_repository(id);")

    cursor.execute("ALTER TABLE reuse_to_prs ADD CONSTRAINT reuse_to_prs_fk1 FOREIGN KEY (pr_id) REFERENCES pull_requests(pr_id);")