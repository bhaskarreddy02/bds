# Reflection Tree Diagram

This diagram maps the possible paths an employee could take through the deterministic reflection tool.

```mermaid
graph TD
    classDef question fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef decision fill:#fff3e0,stroke:#e65100,stroke-width:2px,stroke-dasharray: 5 5;
    classDef reflection fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px;
    classDef bridge fill:#ede7f6,stroke:#4a148c,stroke-width:2px;
    classDef startend fill:#eceff1,stroke:#37474f,stroke-width:3px;

    START("START"):::startend -->|Advances| A1_OPEN("A1_OPEN<br/>(Describe today)"):::question
    
    A1_OPEN -->|"productive / adjusted"| A1_D1("A1_D1<br/>(Route Positive)"):::decision
    A1_OPEN -->|"frustrating / messes"| A1_D1
    
    A1_D1 -->|"positive day"| A1_Q_AGENCY_H("A1_Q_AGENCY_H<br/>(What drove positive outcome?)"):::question
    A1_D1 -->|"negative day"| A1_Q_AGENCY_L("A1_Q_AGENCY_L<br/>(What was initial instinct?)"):::question
    
    A1_Q_AGENCY_H -->|Collects axis1 signals| A1_D2{"A1_D2<br/>(Locus Check)"}:::decision
    A1_Q_AGENCY_L -->|Collects axis1 signals| A1_D2
    
    A1_D2 -->|dominant: internal| A1_R_INT("A1_R_INT<br/>(Internal Reflection)"):::reflection
    A1_D2 -->|dominant: external| A1_R_EXT("A1_R_EXT<br/>(External Reflection)"):::reflection
    
    A1_R_INT -->|Advances| BRIDGE_1_2("BRIDGE_1_2"):::bridge
    A1_R_EXT -->|Advances| BRIDGE_1_2
    
    BRIDGE_1_2 --> A2_OPEN("A2_OPEN<br/>(Interaction feeling)"):::question
    
    A2_OPEN -->|"unacknowledged / annoyed"| A2_D1("A2_D1"):::decision
    A2_OPEN -->|"help / deliverables"| A2_D1
    
    A2_D1 -->|"unacknowledged / annoyed"| A2_Q_ENTITLE("A2_Q_ENTITLE<br/>(Where does expectation come from?)"):::question
    A2_D1 -->|"help / deliverables"| A2_Q_CONTRIB("A2_Q_CONTRIB<br/>(Why take that approach?)"):::question
    
    A2_Q_ENTITLE -->|Collects axis2 signals| A2_D2{"A2_D2<br/>(Orientation Check)"}:::decision
    A2_Q_CONTRIB -->|Collects axis2 signals| A2_D2
    
    A2_D2 -->|dominant: contribution| A2_R_CONTRIB("A2_R_CONTRIB<br/>(Contribution Reflection)"):::reflection
    A2_D2 -->|dominant: entitlement| A2_R_ENTITLE("A2_R_ENTITLE<br/>(Entitlement Reflection)"):::reflection
    #ref tree 
    A2_R_CONTRIB -->|Advances| BRIDGE_2_3("BRIDGE_2_3"):::bridge
    A2_R_ENTITLE -->|Advances| BRIDGE_2_3
    
    BRIDGE_2_3 --> A3_OPEN("A3_OPEN<br/>(Who was center of narrative?)"):::question
    
    A3_OPEN -->|Collects signals implicitly via routing| A3_D1("A3_D1"):::decision
    
    A3_D1 -->|"just me / me & manager"| A3_Q_SELF("A3_Q_SELF<br/>(What if wider perspective?)"):::question
    A3_D1 -->|"team / mission"| A3_Q_ALTRO("A3_Q_ALTRO<br/>(What enables wider perspective?)"):::question
    
    A3_Q_SELF -->|Collects axis3 signals| A3_D2{"A3_D2<br/>(Radius Check)"}:::decision
    A3_Q_ALTRO -->|Collects axis3 signals| A3_D2
    
    A3_D2 -->|dominant: altrocentric| A3_R_ALTRO("A3_R_ALTRO<br/>(Altrocentric Reflection)"):::reflection
    A3_D2 -->|dominant: selfcentric| A3_R_SELF("A3_R_SELF<br/>(Selfcentric Reflection)"):::reflection
    
    A3_R_ALTRO -->|Advances| SUMMARY_PREP("SUMMARY_PREP"):::decision
    A3_R_SELF -->|Advances| SUMMARY_PREP
    
    SUMMARY_PREP -->|Unconditional| SUMMARY("SUMMARY<br/>(Interpolates all path signals)"):::reflection
    
    SUMMARY -->|Advances| END("END"):::startend
```
