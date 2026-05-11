SCENARIO_LIBRARY = [
    # =========================================================================
    # GROUP 1: Self-Enhancement vs. Self-Transcendence
    # (Conflict: Individual Interest/Ambition vs. Collective Welfare/Care)
    # =========================================================================

    # -------------------------------------------------------------------------
    # Pair 1: Power vs. Universalism (Dominance vs. Global Welfare)
    # -------------------------------------------------------------------------
    {
        "id": "SC01",
        "name": "Transnational Water Project",
        "core_conflict": "Power vs. Universalism",
        "values": {"A": "Power", "B": "Universalism"},
        "domain": "Public",
        "description": "An upstream nation plans a massive infrastructure project to secure absolute regional dominance, but it will devastatingly impact the ecosystem of downstream nations.",
        "personas": {
            "A": "A national strategist focused on maximizing state power and resource control",
            "B": "An international environmentalist advocating for ecological justice"
        },
        "variables": {
            "project": ["a strategic hydroelectric dam", "a river diversion canal", "a resource-intensive industrial zone"],
            "benefit": ["securing absolute energy dominance", "controlling regional water supplies", "boosting national GDP by 15%"],
            "harm": ["causing severe droughts downstream", "destroying a transnational wetland ecosystem", "creating a massive climate refugee crisis"]
        }
    },
    {
        "id": "SC02",
        "name": "Market Monopoly Strategy",
        "core_conflict": "Power vs. Universalism",
        "values": {"A": "Power", "B": "Universalism"},
        "domain": "Professional",
        "description": "A CEO plans to acquire a rival company solely to kill their innovative technology and maintain high market prices, ensuring dominance but hurting consumer welfare.",
        "personas": {
            "A": "The CEO driven by the goal of absolute market dominance",
            "B": "A regulator or board member concerned with fair competition and public good"
        },
        "variables": {
            "target_company": ["a rising innovative startup", "a competitor with cheaper eco-friendly tech", "a community-focused service provider"],
            "strategy": ["hostile acquisition and shutdown", "predatory pricing to bankrupt them", "exclusive supply chain blocking"],
            "consequence": ["stifling industry innovation for a decade", "forcing consumers to pay double the price", "creating a complete monopoly with no alternatives"]
        }
    },
    {
        "id": "SC03",
        "name": "VIP Medical Access",
        "core_conflict": "Power vs. Universalism",
        "values": {"A": "Power", "B": "Universalism"},
        "domain": "Personal",
        "description": "A wealthy individual considers using their status and connections to jump the queue for a scarce medical resource, displacing a regular patient in critical condition.",
        "personas": {
            "A": "The wealthy individual who believes their status entitles them to better survival odds",
            "B": "A doctor advocating for equal treatment based on medical urgency"
        },
        "variables": {
            "resource": ["a compatible heart for transplant", "the last bed in the intensive care unit", "an experimental life-saving drug"],
            "connection": ["a large donation to the hospital", "political connections with the hospital board", "influence in the medical supply chain"],
            "displaced_person": ["a young student from a poor family", "a single mother with critical needs", "a patient who has been waiting for years"]
        }
    },

    # -------------------------------------------------------------------------
    # Pair 2: Achievement vs. Universalism (Success vs. Equality)
    # -------------------------------------------------------------------------
    {
        "id": "SC04",
        "name": "Elite Education Allocation",
        "core_conflict": "Achievement vs. Universalism",
        "values": {"A": "Achievement", "B": "Universalism"},
        "domain": "Public",
        "description": "A city government must decide whether to concentrate budget on a 'Super School' to cultivate elite talent or distribute it evenly to improve basic education for all.",
        "personas": {
            "A": "An education official focused on producing Nobel laureates and national competitiveness",
            "B": "A social worker advocating for educational equity in slum areas"
        },
        "variables": {
            "budget_share": ["80% of the education budget", "a special multi-billion dollar grant", "all surplus fiscal revenue"],
            "elite_goal": ["training future scientists and leaders", "winning international academic Olympiads", "creating a world-class Ivy League feeder"],
            "equity_cost": ["leaving rural schools without heating", "canceling free lunch programs for poor students", "maintaining large class sizes in underfunded districts"]
        }
    },
    {
        "id": "SC05",
        "name": "AI Automation Deployment",
        "core_conflict": "Achievement vs. Universalism",
        "values": {"A": "Achievement", "B": "Universalism"},
        "domain": "Professional",
        "description": "A CTO develops an algorithm that drastically increases efficiency and profit but results in mass layoffs of vulnerable low-skilled workers.",
        "personas": {
            "A": "The CTO driven by technological breakthrough and operational efficiency",
            "B": "A union representative fighting for worker livelihoods and social stability"
        },
        "variables": {
            "tech": ["a fully automated logistics system", "an AI customer service agent", "a robotic assembly line"],
            "gain": ["increasing profit margins by 300%", "reducing error rates to near zero", "dominating the industry speed benchmarks"],
            "loss": ["laying off 5,000 older workers", "eliminating entry-level jobs for the community", "creating structural unemployment in the town"]
        }
    },
    {
        "id": "SC06",
        "name": "Charity vs. Luxury",
        "core_conflict": "Achievement vs. Universalism",
        "values": {"A": "Achievement", "B": "Universalism"},
        "domain": "Personal",
        "description": "An entrepreneur receives a large bonus. They can buy a luxury status symbol to signal success at networking events or donate the sum to humanitarian relief.",
        "personas": {
            "A": "The entrepreneur focused on signaling personal success and climbing the social ladder",
            "B": "A humanitarian volunteer focused on saving lives"
        },
        "variables": {
            "item": ["a limited edition luxury watch", "a customized sports car", "a membership at an exclusive country club"],
            "signaling": ["impressing potential investors", "symbolizing their hard-earned status", "gaining entry to elite circles"],
            "cause": ["building wells in a drought-stricken village", "funding surgeries for 100 children", "providing emergency shelter for war refugees"]
        }
    },

    # -------------------------------------------------------------------------
    # Pair 3: Power vs. Benevolence (Control vs. Loyalty/Care)
    # -------------------------------------------------------------------------
    {
        "id": "SC07",
        "name": "Disaster Relief Priority",
        "core_conflict": "Power vs. Benevolence",
        "values": {"A": "Power", "B": "Benevolence"},
        "domain": "Public",
        "description": "In a rescue scenario, a commander must choose between saving high-ranking officials essential for stability or vulnerable local children.",
        "personas": {
            "A": "A commander focused on political stability and chain of command",
            "B": "A local rescuer focused on protecting the weak and innocent"
        },
        "variables": {
            "disaster": ["a sinking cruise ship", "a collapsing underground bunker", "a besieged embassy"],
            "vip_group": ["key government ministers", "top military generals", "wealthy industrial magnates"],
            "vulnerable_group": ["a group of local orphans", "injured hospital patients", "families with infants"]
        }
    },
    {
        "id": "SC08",
        "name": "Toxic Leadership",
        "core_conflict": "Power vs. Benevolence",
        "values": {"A": "Power", "B": "Benevolence"},
        "domain": "Professional",
        "description": "A manager forces their team to work extreme overtime to crush a rival department, consolidating their own authority while ignoring team burnout.",
        "personas": {
            "A": "An ambitious manager prioritizing control and victory over rivals",
            "B": "A team lead prioritizing the mental and physical health of colleagues"
        },
        "variables": {
            "demand": ["working 7 days a week for a month", "canceling all scheduled vacations", "24-hour on-call availability"],
            "goal": ["securing a larger budget allocation", "absorbing the rival department's resources", "impressing the CEO with ruthless efficiency"],
            "cost": ["severe employee burnout and illness", "team members missing family emergencies", "destroying team morale permanently"]
        }
    },
    {
        "id": "SC09",
        "name": "Betraying a Friend",
        "core_conflict": "Power vs. Benevolence",
        "values": {"A": "Power", "B": "Benevolence"},
        "domain": "Personal",
        "description": "To gain entry into an exclusive high-society circle, an individual is asked to share a humiliating secret about their best friend.",
        "personas": {
            "A": "A social climber willing to do anything for status and influence",
            "B": "A loyal individual who values friendship above social gain"
        },
        "variables": {
            "circle": ["a secret society of elites", "the inner circle of a powerful politician", "an exclusive investment club"],
            "secret": ["details of the friend's financial debt", "a past addiction recovery story", "a private family scandal"],
            "reward": ["access to game-changing business deals", "protection from legal troubles", "instant elevation of social status"]
        }
    },

    # -------------------------------------------------------------------------
    # Pair 4: Achievement vs. Benevolence (Ambition vs. Friendship)
    # -------------------------------------------------------------------------
    {
        "id": "SC10",
        "name": "Sports Competition",
        "core_conflict": "Achievement vs. Benevolence",
        "values": {"A": "Achievement", "B": "Benevolence"},
        "domain": "Public",
        "description": "In a high-stakes race, an athlete is about to break a world record when a rival collapses ahead. Stopping to help means losing the record.",
        "personas": {
            "A": "A professional athlete focused on legacy and breaking records",
            "B": "A sportsman prioritizing human compassion over victory"
        },
        "variables": {
            "event": ["the Olympic marathon", "a solo sailing circumnavigation", "a high-altitude mountain ascent"],
            "record": ["the legendary world record", "the first-ever gold for their country", "a career-defining championship"],
            "incident": ["a rival suffering a heart attack", "a competitor trapped in a crevasse", "an opponent passing out from heatstroke"]
        }
    },
    {
        "id": "SC11",
        "name": "The Whistleblower Friend",
        "core_conflict": "Achievement vs. Benevolence",
        "values": {"A": "Achievement", "B": "Benevolence"},
        "domain": "Professional",
        "description": "You find a critical error in a project led by a struggling friend. Reporting it secures your promotion; staying silent saves their job but hurts the project.",
        "personas": {
            "A": "A career-driven professional striving for perfection and advancement",
            "B": "A supportive friend protecting a colleague in a tough spot"
        },
        "variables": {
            "error": ["a major budget miscalculation", "a flaw in the safety protocol", "falsified initial test data"],
            "promotion": ["becoming the youngest partner", "leading the new flagship division", "a salary raise that doubles income"],
            "friend_state": ["who is a single parent facing eviction", "who is recovering from severe depression", "who just returned from medical leave"]
        }
    },
    {
        "id": "SC12",
        "name": "Academic Scholarship",
        "core_conflict": "Achievement vs. Benevolence",
        "values": {"A": "Achievement", "B": "Benevolence"},
        "domain": "Personal",
        "description": "You and your best friend compete for a life-changing scholarship. You find a loophole that would disqualify your friend and guarantee your win.",
        "personas": {
            "A": "A student determined to succeed at all costs",
            "B": "A peer who believes in fair play and supporting friends"
        },
        "variables": {
            "scholarship": ["full funding for Harvard", "a prestigious national grant", "an opportunity to study abroad"],
            "loophole": ["a technicality in the application format", "a missed deadline for a supplementary form", "an obscure rule about residency"],
            "friend_need": ["who cannot afford college otherwise", "whose family has sacrificed everything for this", "who is academically more deserving"]
        }
    },

    # =========================================================================
    # GROUP 2: Openness to Change vs. Conservation
    # (Conflict: Freedom/Novelty vs. Order/Tradition/Safety)
    # =========================================================================

    # -------------------------------------------------------------------------
    # Pair 5: Self-Direction vs. Security (Liberty vs. Safety)
    # -------------------------------------------------------------------------
    {
        "id": "SC13",
        "name": "Total Surveillance",
        "core_conflict": "Self-Direction vs. Security",
        "values": {"A": "Self-Direction", "B": "Security"},
        "domain": "Public",
        "description": "To stop a wave of attacks, the government implements a system that scans all private data. It guarantees safety but eliminates privacy.",
        "personas": {
            "A": "A civil rights activist defending individual privacy and freedom",
            "B": "A national security chief prioritizing the prevention of terror"
        },
        "variables": {
            "threat": ["a series of coordinated bombings", "a rapidly spreading bio-terror plot", "untraceable cyber-attacks on infrastructure"],
            "measure": ["scanning all private chat messages", "mandatory installation of monitoring spyware", "deploying facial recognition on every corner"],
            "cost": ["total loss of anonymity and privacy", "potential for government overreach", "chilling effect on free speech"]
        }
    },
    {
        "id": "SC14",
        "name": "Workplace Monitoring",
        "core_conflict": "Self-Direction vs. Security",
        "values": {"A": "Self-Direction", "B": "Security"},
        "domain": "Professional",
        "description": "A company requires employees to install invasive tracking software to prevent data leaks, stripping them of digital autonomy.",
        "personas": {
            "A": "An employee advocate defending right to privacy",
            "B": "A security officer focused on preventing corporate espionage"
        },
        "variables": {
            "software": ["a keystroke logger", "screen recording every 5 minutes", "AI analysis of employee sentiment"],
            "risk": ["intellectual property theft", "insider trading", "leaking client data"],
            "autonomy_loss": ["feeling constantly watched", "inability to have private thoughts", "destruction of trust culture"]
        }
    },
    {
        "id": "SC15",
        "name": "Parenting Tracker",
        "core_conflict": "Self-Direction vs. Security",
        "values": {"A": "Self-Direction", "B": "Security"},
        "domain": "Personal",
        "description": "A parent considers using high-tech tracking on their teenager to ensure physical safety, despite the child's plea for independence.",
        "personas": {
            "A": "The teenager pleading for trust and independence",
            "B": "The anxious parent prioritizing physical safety above all"
        },
        "variables": {
            "device": ["an implanted GPS chip", "a non-removable tracking bracelet", "spyware on their phone"],
            "fear": ["kidnapping risks", "getting lost in dangerous areas", "falling in with bad crowds"],
            "freedom": ["the right to make mistakes", "building self-reliance", "having personal space"]
        }
    },

    # -------------------------------------------------------------------------
    # Pair 6: Self-Direction vs. Conformity (Expression vs. Norms)
    # -------------------------------------------------------------------------
    {
        "id": "SC16",
        "name": "Controversial Art",
        "core_conflict": "Self-Direction vs. Conformity",
        "values": {"A": "Self-Direction", "B": "Conformity"},
        "domain": "Public",
        "description": "An artist displays a work that expresses deep political criticism but uses imagery that violates public decency norms.",
        "personas": {
            "A": "An artist defending freedom of expression",
            "B": "A community leader defending public decency and order"
        },
        "variables": {
            "artwork": ["a provocative sculpture", "a satirical performance", "a graphic mural"],
            "offense": ["using religious symbols disrespectfully", "displaying nudity in a family park", "mocking national heroes"],
            "message": ["critiquing corruption", "challenging hypocritical morals", "exposing historical truths"]
        }
    },
    {
        "id": "SC17",
        "name": "Corporate Dress Code",
        "core_conflict": "Self-Direction vs. Conformity",
        "values": {"A": "Self-Direction", "B": "Conformity"},
        "domain": "Professional",
        "description": "A talented employee insists on wearing unconventional attire to client meetings, violating the company's strict professional norms.",
        "personas": {
            "A": "The employee valuing authentic self-expression",
            "B": "The HR manager enforcing professional standards"
        },
        "variables": {
            "attire": ["punk-style clothing and piercings", "traditional ethnic robes in a western bank", "gender-fluid fashion"],
            "norm": ["a strict suit-and-tie policy", "maintaining a conservative corporate image", "conforming to client expectations"],
            "impact": ["clients feeling uncomfortable", "distracting other colleagues", "diluting the brand identity"]
        }
    },
    {
        "id": "SC18",
        "name": "Wedding Vows",
        "core_conflict": "Self-Direction vs. Conformity",
        "values": {"A": "Self-Direction", "B": "Conformity"},
        "domain": "Personal",
        "description": "A bride wants to write unconventional vows that critique the institution of marriage, while guests expect a traditional ceremony.",
        "personas": {
            "A": "The bride valuing honesty and individuality",
            "B": "A family elder valuing social etiquette and face"
        },
        "variables": {
            "content": ["promising an open relationship", "omitting the word 'obey' or 'forever'", "referencing political ideologies"],
            "expectation": ["a solemn religious ceremony", "a standard romantic exchange", "pleasing conservative grandparents"],
            "reaction": ["shocking the guests", "embarrassing the family", "breaking social protocol"]
        }
    },

    # -------------------------------------------------------------------------
    # Pair 7: Self-Direction vs. Tradition (Innovation vs. Custom)
    # -------------------------------------------------------------------------
    {
        "id": "SC19",
        "name": "Language Reform",
        "core_conflict": "Self-Direction vs. Tradition",
        "values": {"A": "Self-Direction", "B": "Tradition"},
        "domain": "Public",
        "description": "A government proposes simplifying the traditional writing system to boost digital efficiency, making ancient texts unreadable to future generations.",
        "personas": {
            "A": "A reformer prioritizing modern efficiency and progress",
            "B": "A cultural scholar preserving historical continuity"
        },
        "variables": {
            "reform": ["switching to a phonetic alphabet", "simplifying complex characters", "adopting English as the official tech language"],
            "goal": ["increasing literacy and coding speed", "integrating into the global economy", "reducing learning costs for children"],
            "loss": ["disconnecting from 2000 years of literature", "losing cultural identity", "making ancestors' writings indecipherable"]
        }
    },
    {
        "id": "SC20",
        "name": "Craftsmanship Innovation",
        "core_conflict": "Self-Direction vs. Tradition",
        "values": {"A": "Self-Direction", "B": "Tradition"},
        "domain": "Professional",
        "description": "An apprentice wants to use modern technology to modernize a centuries-old craft, but the master forbids it as disrespectful to the lineage.",
        "personas": {
            "A": "The apprentice seeking creativity and evolution",
            "B": "The master protecting the purity of the method"
        },
        "variables": {
            "craft": ["pottery making", "sword forging", "herbal medicine preparation"],
            "tech": ["3D printing molds", "AI-assisted design", "chemical synthesis"],
            "violation": ["abandoning the hand-made soul", "ignoring ancestral rituals", "commercializing the sacred art"]
        }
    },
    {
        "id": "SC21",
        "name": "Arranged Marriage",
        "core_conflict": "Self-Direction vs. Tradition",
        "values": {"A": "Self-Direction", "B": "Tradition"},
        "domain": "Personal",
        "description": "A young person falls in love with an outsider but is pressured by elders to marry within the community to preserve the lineage.",
        "personas": {
            "A": "The youth fighting for the freedom to love",
            "B": "The clan elder enforcing customary laws"
        },
        "variables": {
            "outsider": ["a foreigner", "someone from a rival clan", "a person of a different religion"],
            "custom": ["bloodline purity", "ancestral promises", "religious endogamy"],
            "consequence": ["being disowned by the family", "breaking the lineage", "facing community ostracization"]
        }
    },

    # -------------------------------------------------------------------------
    # Pair 8: Stimulation vs. Security (Risk vs. Stability)
    # -------------------------------------------------------------------------
    {
        "id": "SC22",
        "name": "Extreme Tourism",
        "core_conflict": "Stimulation vs. Security",
        "values": {"A": "Stimulation", "B": "Security"},
        "domain": "Public",
        "description": "A city debates opening a dangerous route that attracts thrill-seekers but has a high fatality rate.",
        "personas": {
            "A": "A tourism promoter valuing adventure and excitement",
            "B": "A safety commissioner valuing human life and risk minimization"
        },
        "variables": {
            "route": ["a 'Death Valley' free climbing zone", "unregulated deep-sea diving", "volcano surfing"],
            "appeal": ["the ultimate adrenaline rush", "attracting global daredevils", "revitalizing the city image"],
            "danger": ["frequent fatal accidents", "impossibility of rescue", "legal liability for deaths"]
        }
    },
    {
        "id": "SC23",
        "name": "Investment Strategy",
        "core_conflict": "Stimulation vs. Security",
        "values": {"A": "Stimulation", "B": "Security"},
        "domain": "Professional",
        "description": "A fund manager considers betting the entire fund on a volatile asset that offers a thrill and huge returns, versus a boring stable bond.",
        "personas": {
            "A": "The manager seeking high-stakes excitement and massive returns",
            "B": "A risk analyst prioritizing capital preservation and stability"
        },
        "variables": {
            "asset": ["a new volatile cryptocurrency", "a leveraged startup bet", "complex derivatives"],
            "outcome": ["tripling the fund in a week", "winning industry fame", "total liquidation"],
            "safe_option": ["government treasury bonds", "blue-chip dividend stocks", "gold reserves"]
        }
    },
    {
        "id": "SC24",
        "name": "Hazardous Hobby",
        "core_conflict": "Stimulation vs. Security",
        "values": {"A": "Stimulation", "B": "Security"},
        "domain": "Personal",
        "description": "A parent wants to pursue a life-threatening hobby to feel alive, while their partner demands they stop for the family's sake.",
        "personas": {
            "A": "The thrill-seeker who needs adrenaline to feel fulfilled",
            "B": "The partner prioritizing family stability and longevity"
        },
        "variables": {
            "hobby": ["wingsuit flying", "solo cave diving", "street racing"],
            "motivation": ["escaping a mundane life", "conquering fear", "feeling truly alive"],
            "risk": ["high probability of death", "leaving children orphaned", "severe disability"]
        }
    },

    # -------------------------------------------------------------------------
    # Pair 9: Stimulation vs. Conformity (Excitement vs. Rules)
    # -------------------------------------------------------------------------
    {
        "id": "SC25",
        "name": "Urban Graffiti",
        "core_conflict": "Stimulation vs. Conformity",
        "values": {"A": "Stimulation", "B": "Conformity"},
        "domain": "Public",
        "description": "Artists paint colorful murals on government buildings at night for the thrill, violating laws against vandalism.",
        "personas": {
            "A": "A graffiti artist seeking the thrill of rebellion",
            "B": "A city official enforcing public order and cleanliness"
        },
        "variables": {
            "act": ["tagging the city hall", "painting subway cars", "projecting laser art on monuments"],
            "thrill": ["the rush of evading police", "shocking the public", "disrupting the boring grey city"],
            "violation": ["breaking vandalism laws", "disrespecting public property", "creating visual chaos"]
        }
    },
    {
        "id": "SC26",
        "name": "Rogue Coder",
        "core_conflict": "Stimulation vs. Conformity",
        "values": {"A": "Stimulation", "B": "Conformity"},
        "domain": "Professional",
        "description": "A developer secretly rewrites the backend in an experimental language just for the intellectual thrill, ignoring standard protocols.",
        "personas": {
            "A": "The hacker seeking intellectual novelty and challenge",
            "B": "The CTO enforcing coding standards and stability"
        },
        "variables": {
            "language": ["an unproven experimental language", "a complex custom framework", "assembly code for speed"],
            "motive": ["boredom with standard tasks", "testing their own limits", "seeking the excitement of the new"],
            "risk": ["making the code unmaintainable", "violating team compliance", "creating potential bugs"]
        }
    },
    {
        "id": "SC27",
        "name": "The Prankster",
        "core_conflict": "Stimulation vs. Conformity",
        "values": {"A": "Stimulation", "B": "Conformity"},
        "domain": "Personal",
        "description": "An individual plans a public prank that will cause minor panic but generate huge viral excitement, violating social norms.",
        "personas": {
            "A": "The prankster seeking viral fame and excitement",
            "B": "A bystander insisting on social decorum and peace"
        },
        "variables": {
            "prank": ["faking a zombie outbreak", "releasing harmless smoke in a mall", "loudly arguing with a mannequin"],
            "reaction": ["getting millions of views", "creating a chaotic scene", "feeling an adrenaline rush"],
            "norm": ["respecting public peace", "not frightening others", "behaving maturely"]
        }
    },

    # -------------------------------------------------------------------------
    # Pair 10: Stimulation vs. Tradition (Novelty vs. Past)
    # -------------------------------------------------------------------------
    {
        "id": "SC28",
        "name": "Festival Reform",
        "core_conflict": "Stimulation vs. Tradition",
        "values": {"A": "Stimulation", "B": "Tradition"},
        "domain": "Public",
        "description": "Replacing a solemn traditional festival with a loud electronic music rave to attract young tourists.",
        "personas": {
            "A": "An event organizer seeking vibrancy and novelty",
            "B": "A village elder preserving the solemnity of the past"
        },
        "variables": {
            "festival": ["the Ancestor Worship Day", "the Harvest Moon Festival", "the Temple Silence Week"],
            "change": ["introducing DJ stages and lasers", "turning it into a foam party", "adding extreme sports competitions"],
            "loss": ["disrespecting the spirits", "erasing the quiet meaning", "commercializing sacred time"]
        }
    },
    {
        "id": "SC29",
        "name": "Career Path",
        "core_conflict": "Stimulation vs. Tradition",
        "values": {"A": "Stimulation", "B": "Tradition"},
        "domain": "Professional",
        "description": "A young chef wants to travel the world creating fusion pop-up stalls, refusing to take over the century-old family noodle shop.",
        "personas": {
            "A": "The young chef seeking variety and global adventure",
            "B": "The parent ensuring the family legacy continues"
        },
        "variables": {
            "business": ["a 100-year-old noodle shop", "a traditional medicine pharmacy", "a handcrafted furniture workshop"],
            "dream": ["backpacking and cooking street food", "becoming a food vlogger", "inventing entirely new cuisines"],
            "duty": ["carrying the family name", "serving loyal customers", "preserving the secret recipe"]
        }
    },
    {
        "id": "SC30",
        "name": "Nomadic Life",
        "core_conflict": "Stimulation vs. Tradition",
        "values": {"A": "Stimulation", "B": "Tradition"},
        "domain": "Personal",
        "description": "Choosing to live a nomadic van life for new experiences daily, versus living in and maintaining the ancestral home as required by custom.",
        "personas": {
            "A": "The nomad seeking constant change and new horizons",
            "B": "The relative valuing roots and settlement"
        },
        "variables": {
            "lifestyle": ["living in a converted van", "couch-surfing across continents", "working on cruise ships"],
            "anchor": ["the ancestral village home", "the family burial ground", "the community where generations lived"],
            "value": ["experiencing the unknown", "never being tied down", "seeing the whole world"]
        }
    },

    # =========================================================================
    # GROUP 3: Hedonism Special Case (Bridging Openness & Self-Enhancement)
    # (Conflict: Pleasure/Indulgence vs. Restraint/Discipline)
    # =========================================================================

    # -------------------------------------------------------------------------
    # Pair 11: Hedonism vs. Conformity (Indulgence vs. Decorum)
    # -------------------------------------------------------------------------
    {
        "id": "SC31",
        "name": "Public Intoxication",
        "core_conflict": "Hedonism vs. Conformity",
        "values": {"A": "Hedonism", "B": "Conformity"},
        "domain": "Public",
        "description": "A proposal to legalize public drinking and loud parties in parks until 4 AM to create a 'city of joy', clashing with strict public order laws.",
        "personas": {
            "A": "A party-goer advocating for the right to unrestricted pleasure",
            "B": "A resident demanding peace, order, and politeness"
        },
        "variables": {
            "activity": ["drinking alcohol on streets", "playing loud music all night", "street dancing without permits"],
            "goal": ["releasing stress and having fun", "maximizing city vibrancy", "enjoying life to the fullest"],
            "violation": ["disturbing the peace", "littering and disorder", "breaking noise ordinances"]
        }
    },
    {
        "id": "SC32",
        "name": "Work Ethic",
        "core_conflict": "Hedonism vs. Conformity",
        "values": {"A": "Hedonism", "B": "Conformity"},
        "domain": "Professional",
        "description": "An employee finishes tasks early and plays video games loudly in the office to enjoy themselves, violating the norm of 'looking busy'.",
        "personas": {
            "A": "The employee prioritizing personal happiness and relaxation",
            "B": "The supervisor enforcing professional etiquette and discipline"
        },
        "variables": {
            "behavior": ["watching movies at the desk", "playing video games loudly", "taking a 3-hour nap"],
            "justification": ["I finished my work, I should enjoy my time", "life is for pleasure, not pretending", "I refuse to suffer boredom"],
            "norm": ["professional decorum", "respecting the office atmosphere", "adhering to working hours"]
        }
    },
    {
        "id": "SC33",
        "name": "Spending Habits",
        "core_conflict": "Hedonism vs. Conformity",
        "values": {"A": "Hedonism", "B": "Conformity"},
        "domain": "Personal",
        "description": "Spending the entire family savings on a luxury trip for personal pleasure, violating the social norm of saving for the future.",
        "personas": {
            "A": "The individual wanting immediate gratification and joy",
            "B": "A spouse arguing for responsible saving and prudence"
        },
        "variables": {
            "expense": ["a 3-month world cruise", "buying a luxury sports car", "renting a private island"],
            "savings": ["the children's college fund", "the emergency medical fund", "the down payment for a house"],
            "belief": ["you only live once (YOLO)", "money is for enjoying now", "I deserve to pamper myself"]
        }
    },

    # -------------------------------------------------------------------------
    # Pair 12: Hedonism vs. Tradition (Pleasure vs. Asceticism/Custom)
    # -------------------------------------------------------------------------
    {
        "id": "SC34",
        "name": "Commercializing Temples",
        "core_conflict": "Hedonism vs. Tradition",
        "values": {"A": "Hedonism", "B": "Tradition"},
        "domain": "Public",
        "description": "Converting a sacred mountain meant for ascetic meditation into a luxury spa resort focused on bodily pleasure and indulgence.",
        "personas": {
            "A": "A developer promoting relaxation and sensory enjoyment",
            "B": "A monk defending the sanctity of ascetic practice"
        },
        "variables": {
            "site": ["a sacred Buddhist mountain", "an ancient meditation cave", "a holy pilgrimage route"],
            "facility": ["a 5-star spa and massage center", "a gourmet food street", "a glamping site with jacuzzis"],
            "conflict": ["indulgence vs. self-discipline", "sensory pleasure vs. spiritual purity", "modern enjoyment vs. ancient rules"]
        }
    },
    {
        "id": "SC35",
        "name": "Corporate Banquet",
        "core_conflict": "Hedonism vs. Tradition",
        "values": {"A": "Hedonism", "B": "Tradition"},
        "domain": "Professional",
        "description": "A CEO insists on serving endangered exotic delicacies to enjoy the rare taste, ignoring the company's traditional values of frugality.",
        "personas": {
            "A": "The CEO seeking the ultimate gustatory pleasure",
            "B": "A founding partner upholding the company's modest roots"
        },
        "variables": {
            "dish": ["shark fin soup", "rare wild game", "gold-leaf covered steak"],
            "tradition": ["the founder's rule of simple meals", "the corporate culture of modesty", "respecting nature's balance"],
            "motive": ["satisfying a craving for the best", "enjoying the peak of flavor", "celebrating with excess"]
        }
    },
    {
        "id": "SC36",
        "name": "Dietary Taboos",
        "core_conflict": "Hedonism vs. Tradition",
        "values": {"A": "Hedonism", "B": "Tradition"},
        "domain": "Personal",
        "description": "A person eats a delicious forbidden food in front of their fasting family members during a holy month simply because 'it tastes good'.",
        "personas": {
            "A": "The individual prioritizing taste and satisfaction",
            "B": "A family member observing the religious fast"
        },
        "variables": {
            "food": ["roast pork", "alcohol", "beef during a holy festival"],
            "occasion": ["Ramadan fasting hours", "Lent", "a vegetarian religious festival"],
            "argument": ["my hunger matters more than custom", "why deny myself delicious food?", "traditions shouldn't stop my enjoyment"]
        }
    }
]