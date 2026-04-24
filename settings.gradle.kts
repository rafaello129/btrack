pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "btrack-mobile"

include(
    ":app",
    ":core-ui",
    ":core-analysis",
    ":feature-capture",
    ":feature-results",
    ":feature-history",
    ":data-local",
    ":feature-patients",
    ":feature-records",
    ":feature-dashboard",
    ":feature-telemed",
)
