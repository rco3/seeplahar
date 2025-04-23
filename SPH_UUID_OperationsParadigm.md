# Farm Operations System with Pre-printed QR Labels - Comprehensive Summary

## System Architecture Overview

The farm operations system utilizes Django's web framework to create a URL structure that maps UUIDs to entity details while supporting QR code scanning for rapid field operations. The core innovation is using pre-printed QR labels to streamline harvest tracking without requiring field printing equipment.

## URL Structure and UUID Implementation

### URL Design
- Universal detail URL format: `https://robs_awesome_garden.com/{UUID}`
- This URL serves two purposes:
  1. Customer-facing information about any entity (plant, harvest, seed)
  2. Internal system identifier for operations and scanning

### UUID Implementation
- All major entities (Planting, Harvest, SeedLot, etc.) use UUID primary keys
- UUIDs provide globally unique, non-sequential identifiers
- UUIDs eliminate the risk of ID collisions when importing external data
- URL extraction directly yields the entity's database key

## QR Code System

### Types of QR Codes
1. **Entity QR Codes**: Link to detail pages for specific items
   - Format: `https://robs_awesome_garden.com/{UUID}`
   - Used for plants, harvests, seedlots, seedling batches

2. **Operation QR Codes**: Launch specific workflows
   - Format: `https://robs_awesome_garden.com/farm/operations/{operation_name}/`
   - Example: `https://robs_awesome_garden.com/farm/operations/harvest/`

### Pre-printed QR Label Approach
1. **Preparation Phase**:
   - Generate placeholder records with UUIDs (Harvests, Plants, SeedLots)
   - Pre-print waterproof QR labels for each UUID
   - Store in field-ready container

2. **Field Application**:
   - Take appropriate pre-printed labels to site
   - Scan source entity QR code (e.g., Planting)
   - Scan unused target QR label (e.g., Harvest)
   - System links these two entities
   - Apply label to container or plant marker

3. **Post-Processing Updates**:
   - At processing area, scan entity QR code
   - Record additional details (weight, quality, etc.)
   - Print updated detailed label with this information
   - Replace field label with detailed version

## Core Workflows

### Harvest Operation
1. Scan "Harvest" operation QR from dashboard
2. Scan Planting QR code to identify source
3. Scan pre-printed Harvest QR to create link
4. Apply temporary Harvest QR to container
5. At processing station, scan Harvest QR again
6. Enter/confirm weight and quality details
7. Print updated detailed Harvest label
8. Apply final label to storage container

### Planting Operation
1. Take batch of pre-printed Plant QR labels to field
2. Scan "Plant" operation QR from dashboard
3. Scan SeedlingBatch QR as source
4. For each transplant:
   - Scan unused Plant QR 
   - System links this Plant to SeedlingBatch
   - Apply label to field marker
5. System creates multiple Planting records in batch mode

### SeedLot Creation (Separate Process)
1. Scan "Seed Collection" operation QR
2. Scan Harvest QR to identify source
3. Enter seed preparation details and quantity
4. System creates SeedLot record linked to source Harvest
5. Print SeedLot QR label for seed container

### External Acquisition
1. Scan "External Acquisition" operation QR
2. Select entity type (SeedLot, SeedlingBatch, Planting, Harvest)
3. Enter source partner information
4. Scan pre-printed entity QR code
5. Enter variety and descriptive information
6. Print detailed label for the acquired item

## Data Model Relationships

- **SeedLots** derive from:
  - Harvests (collected seeds, processed separately after harvest)
  - External partners (purchases, trades, gifts)

- **Harvests** derive from:
  - Plantings (from your farm)
  - External partners (purchases, trades, gifts)

- **Plantings** derive from:
  - SeedLots (direct seeding)
  - SeedlingBatches (transplanted seedlings)
  - External partners (purchased plants)

- **SeedlingBatches** derive from:
  - SeedLots
  - External partners (purchased seedlings)

## Technical Implementation Details

### View Structure
1. **Dashboard View** - Shows operation options with QR codes
2. **Operation Views** - Handle scanning of entity QRs
3. **Link Views** - Connect entities (e.g., link Harvest to Planting)
4. **Batch Link Views** - Handle multiple entity links (e.g., SeedlingBatch to multiple Plants)
5. **Detail Views** - Show entity information via UUID lookup
6. **QR Generation Views** - Create QR codes for operations and entities
7. **Label Update Views** - Generate detailed labels after processing

### Key Database Models
- Planting - Represents plants growing in specific locations
- Harvest - Records yield from Plantings with quantity and date
- SeedLot - Contains seeds with variety and source information
- SeedlingBatch - Groups of seedlings from a specific SeedLot

### Security Considerations
- UUID obscures sequential IDs that could be guessed
- Customer context ensures data isolation between farm tenants
- Link operations validate entity relationships before creating connections

## Physical Infrastructure

### QR Scanning Options
1. **Mobile Device** - Using device camera and web app
2. **USB Barcode Scanner** - Connected to computer/tablet
3. **Bluetooth Scanner** - For more mobile operations

### Processing Station
- Digital scale with computer/USB connection
- Computer or tablet with QR scanner
- Label printer for detailed permanent labels
- Optional webcam for photo documentation

## Advantages of This Approach

1. **Workflow Efficiency**
   - Field operations require minimal equipment
   - Pre-printed QRs eliminate tech failures in field
   - Two-phase labeling separates field collection from detailed processing
   - Batch operations streamline planting many items

2. **Data Integrity**
   - Direct scanning eliminates manual data entry errors
   - Automatic linking maintains proper relationships
   - Complete traceability from seed to harvest

3. **Flexibility**
   - Works with mobile devices or dedicated scanners
   - Accommodates external inputs at any stage of production
   - Separates time-sensitive field operations from detailed processing
   - Scale from small operation to larger production

4. **Customer Engagement**
   - QR codes provide customer access to product history
   - Same infrastructure serves both operational and marketing needs
   - Detailed labels can include variety information and usage tips

This system creates a comprehensive digital twin of your physical farm operations, maintaining the connections between entities while streamlining the recording process through strategic use of pre-printed QR codes, batch operations, and a two-phase labeling approach that separates field collection from detailed processing.