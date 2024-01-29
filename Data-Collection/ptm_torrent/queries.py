GITHUB_TOKEN = "GITHUB TOKEN HERE"

# Obtained and modified from https://gist.github.com/MichaelCurrin/6777b91e6374cdb5662b64b8249070ea
FILE_QUERY = """
query RepoFiles($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    object(expression: "HEAD:") {
      ... on Tree {
        entries {
          name
          
          object {
            ... on Blob {
              byteSize
              text
            }
          }
        }
      }
    }
  }
}
"""

# Obtained and modified from https://gist.github.com/MichaelCurrin/6777b91e6374cdb5662b64b8249070ea
CONFIG_QUERY="""
query RepoFiles($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    licenseInfo {
      id
      name
      key
    }
    object(expression: "HEAD:contrib_src/model/config.json") {
        ... on Blob {
          byteSize
          text
        }
    }
  }
}
"""

LICENSE_QUERY="""
query RepoFiles($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    licenseInfo {
      id
      name
      key
    }
  }
}
"""

DEPENDENCY_QUERY = """
query listRepos($queryString:String!){
  #First thing we do is check the rate limit
  rateLimit{
    cost
    remaining
    resetAt
  }
  # We then search all repositories for ones made in the last year
  # that are public and not archived, and have the topic model-hub
  search(query:$queryString, type:REPOSITORY, first:1){
    # We get the total count of repositories that match our query
    repositoryCount
    # We get the pageInfo object, which contains information about the
    # current page, such as the endCursor and startCursor
    pageInfo{
     endCursor
     startCursor
    }
    # We get the edges object, which contains the nodes and the cursor
    # for each node
    edges{
      node{
        # We get the repository object, which contains information about
        # the repository, such as the name, description, and url
        ... on Repository {
          id
          name
          # For each repository, we get the dependency graph manifest
          dependencyGraphManifests {
            # We get the nodes, which contains the dependencies
            edges {
              node {
                # We get the dependencies object, which contains information
                # about the dependencies, such as the package manager, and
                # the dependencies themselves
                dependencies{
                  # We get the totalCount of dependencies
                  totalCount
                  # We get the nodes, which contains the dependencies
                  nodes{
                    # We get the dependency object, which is a Repository
                    # object, which contains information about the repository
                    repository {
                      id
                      name
                      repositoryTopics(first:100) {
                        nodes {
                          ... on RepositoryTopic {
                            topic {
                              name
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
"""

SCHEMA_QUERY = """
query {
  __schema{
    types {
      name
      kind
      description
      fields {
        name
        type {
          name
        }
        description
      }
    }
  }
}
"""

TYPE_QUERY = """
query {
  __type(name: "DependencyGraphManifest"){
    name
    kind
    description
    fields {
      name
      type {
        kind
        name
      }
      description
    }
  }
}
"""