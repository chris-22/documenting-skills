# block-beta — Appian Conventions

## When to use
- Site navigation map (grid layout)
- Better than flowchart when auto-layout produces confusing results

## Appian Sites color conventions
```
classDef siteHeader fill:#EB5757,color:#fff,font-weight:bold
classDef page fill:#2D9CDB,color:#fff
```

## Appian Sites navigation style template
```
block-beta
    columns 4

    block:main_site:4
        columns 4
        main_title["APP_MainPortal /app-portal"]:4
        p1["Home\n(Tempo Report)"]
        p2["Pending Tasks\n(Interface)"]
        p3["Reports\n(Process Model)"]
        p4["Settings\n(Process Model)"]
    end

    space:4

    block:module_a:2
        columns 2
        mod_a_title["APP_ModuleA /app-module-a"]:2
        p5["Search"]
        p6["Create New"]
    end

    block:module_b:2
        columns 2
        mod_b_title["APP_ModuleB /app-module-b"]:2
        p7["Search Items"]
        p8["New Item"]
    end

    classDef siteHeader fill:#EB5757,color:#fff,font-weight:bold
    classDef page fill:#2D9CDB,color:#fff
    class main_title,mod_a_title,mod_b_title siteHeader
    class p1,p2,p3,p4,p5,p6,p7,p8 page
```
