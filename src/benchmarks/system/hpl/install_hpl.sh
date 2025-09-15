#!/bin/bash

# HPL Installation Script for REPACSS Power-aware HPC Benchmarking
# Downloads and extracts the latest HPL version, sets up build directories

set -e

# Configuration
HPL_VERSION="2.3"
HPL_URL="https://www.netlib.org/benchmark/hpl/hpl-${HPL_VERSION}.tar.gz"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HPL_DIR="${SCRIPT_DIR}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are available
check_dependencies() {
    log_info "Checking dependencies..."
    
    local missing_deps=()
    
    if ! command -v wget &> /dev/null && ! command -v curl &> /dev/null; then
        missing_deps+=("wget or curl")
    fi
    
    if ! command -v tar &> /dev/null; then
        missing_deps+=("tar")
    fi
    
    if ! command -v make &> /dev/null; then
        missing_deps+=("make")
    fi
    
    if ! command -v mpicc &> /dev/null; then
        log_warn "mpicc not found. Make sure MPI is installed and in PATH."
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        log_error "Please install the missing dependencies and try again."
        exit 1
    fi
    
    log_info "All dependencies found."
}

# Download and extract HPL source
download_hpl() {
    local source_dir="${HPL_DIR}/source-${HPL_VERSION}"
    
    if [ -d "$source_dir" ]; then
        log_warn "Source directory $source_dir already exists. Skipping download."
        return 0
    fi
    
    log_info "Downloading HPL ${HPL_VERSION} from ${HPL_URL}..."
    
    local temp_file="${HPL_DIR}/hpl-${HPL_VERSION}.tar.gz"
    
    # Download using wget or curl
    if command -v wget &> /dev/null; then
        wget -O "$temp_file" "$HPL_URL"
    elif command -v curl &> /dev/null; then
        curl -L -o "$temp_file" "$HPL_URL"
    fi
    
    if [ ! -f "$temp_file" ]; then
        log_error "Failed to download HPL source"
        exit 1
    fi
    
    log_info "Extracting HPL source to $source_dir..."
    mkdir -p "$source_dir"
    tar -xzf "$temp_file" -C "$source_dir" --strip-components=1
    
    # Clean up
    rm "$temp_file"
    
    log_info "HPL source extracted successfully."
}

# Create build directories for different partitions
create_build_dirs() {
    log_info "Creating build directories for REPACSS partitions..."
    
    # Create build directories
    local build_dirs=("build-zen4" "build-h100")
    
    for build_dir in "${build_dirs[@]}"; do
        local full_path="${HPL_DIR}/${build_dir}"
        if [ -d "$full_path" ]; then
            log_warn "Build directory $full_path already exists. Skipping."
        else
            mkdir -p "$full_path"
            log_info "Created build directory: $full_path"
        fi
    done
}

# Create Makefile templates for different architectures
create_makefile_templates() {
    log_info "Creating Makefile templates for different architectures..."
    
    # Zen4 (AMD EPYC 9754) template
    cat > "${HPL_DIR}/Make.zen4" << 'EOF'
# HPL Makefile for AMD EPYC 9754 (Zen4) - REPACSS CPU Nodes
# 2 CPUs/Node, 256 Cores/Node, 1.5TB Memory/Node

TOPdir       = $(PWD)
INCdir       = $(TOPdir)/include
BINdir       = $(TOPdir)/bin/$(PLAT)
LIBdir       = $(TOPdir)/lib/$(PLAT)
HPLlib       = $(LIBdir)/libhpl.a

MPdir        = /usr/lib/x86_64-linux-gnu/openmpi
MPinc        = -I$(MPdir)/include
MPlib        = $(MPdir)/lib/libmpi.so

LAdir        = /usr/lib/x86_64-linux-gnu
LAinc        = 
LAlib        = -lblas -llapack

HPL_INCLUDES = -I$(INCdir) -I$(INCdir)/$(ARCH) $(LAinc) $(MPinc)
HPL_LIBS     = $(HPLlib) $(LAlib) $(MPlib)

HPL_OPTS     = -DHPL_CALL_CBLAS
HPL_DEFS     = $(HPL_OPTS) $(HPL_INCLUDES)

CC           = mpicc
CCNOOPT      = $(HPL_DEFS)
CCFLAGS      = $(HPL_DEFS) -O3 -march=znver4 -mtune=znver4 -fopenmp

LINKER       = mpicc
LINKFLAGS    = $(CCFLAGS)

ARCHIVER     = ar
ARFLAGS      = r
RANLIB       = echo
EOF

    # H100 (Intel Xeon Gold 6448Y) template
    cat > "${HPL_DIR}/Make.h100" << 'EOF'
# HPL Makefile for Intel Xeon Gold 6448Y - REPACSS GPU Nodes
# 2 CPUs/Node, 64 Cores/Node, 512GB Memory/Node, 4x NVIDIA H100 NVL

TOPdir       = $(PWD)
INCdir       = $(TOPdir)/include
BINdir       = $(TOPdir)/bin/$(PLAT)
LIBdir       = $(TOPdir)/lib/$(PLAT)
HPLlib       = $(LIBdir)/libhpl.a

MPdir        = /usr/lib/x86_64-linux-gnu/openmpi
MPinc        = -I$(MPdir)/include
MPlib        = $(MPdir)/lib/libmpi.so

LAdir        = /usr/lib/x86_64-linux-gnu
LAinc        = 
LAlib        = -lblas -llapack

HPL_INCLUDES = -I$(INCdir) -I$(INCdir)/$(ARCH) $(LAinc) $(MPinc)
HPL_LIBS     = $(HPLlib) $(LAlib) $(MPlib)

HPL_OPTS     = -DHPL_CALL_CBLAS
HPL_DEFS     = $(HPL_OPTS) $(HPL_INCLUDES)

CC           = mpicc
CCNOOPT      = $(HPL_DEFS)
CCFLAGS      = $(HPL_DEFS) -O3 -march=skylake-avx512 -mtune=skylake-avx512 -fopenmp

LINKER       = mpicc
LINKFLAGS    = $(CCFLAGS)

ARCHIVER     = ar
ARFLAGS      = r
RANLIB       = echo
EOF

    log_info "Created Makefile templates: Make.zen4, Make.h100"
}

# Create build scripts for each partition
create_build_scripts() {
    log_info "Creating build scripts for each partition..."
    
    # Zen4 build script
    cat > "${HPL_DIR}/build_zen4.sh" << 'EOF'
#!/bin/bash
# Build HPL for AMD EPYC 9754 (Zen4) - REPACSS CPU Nodes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${SCRIPT_DIR}/source-2.3"
BUILD_DIR="${SCRIPT_DIR}/build-zen4"

if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory $SOURCE_DIR not found. Run install_hpl.sh first."
    exit 1
fi

echo "Building HPL for Zen4 (AMD EPYC 9754)..."
echo "Source: $SOURCE_DIR"
echo "Build:  $BUILD_DIR"

cd "$BUILD_DIR"

# Copy source files
cp -r "$SOURCE_DIR"/* .

# Copy Makefile template
cp "${SCRIPT_DIR}/Make.zen4" ./Make.Linux_Intel64

# Configure and build
make arch=Linux_Intel64

echo "Build completed. Binary: $BUILD_DIR/bin/Linux_Intel64/xhpl"
EOF

    # H100 build script
    cat > "${HPL_DIR}/build_h100.sh" << 'EOF'
#!/bin/bash
# Build HPL for Intel Xeon Gold 6448Y - REPACSS GPU Nodes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${SCRIPT_DIR}/source-2.3"
BUILD_DIR="${SCRIPT_DIR}/build-h100"

if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory $SOURCE_DIR not found. Run install_hpl.sh first."
    exit 1
fi

echo "Building HPL for H100 (Intel Xeon Gold 6448Y)..."
echo "Source: $SOURCE_DIR"
echo "Build:  $BUILD_DIR"

cd "$BUILD_DIR"

# Copy source files
cp -r "$SOURCE_DIR"/* .

# Copy Makefile template
cp "${SCRIPT_DIR}/Make.h100" ./Make.Linux_Intel64

# Configure and build
make arch=Linux_Intel64

echo "Build completed. Binary: $BUILD_DIR/bin/Linux_Intel64/xhpl"
EOF

    # Make scripts executable
    chmod +x "${HPL_DIR}/build_zen4.sh"
    chmod +x "${HPL_DIR}/build_h100.sh"
    
    log_info "Created build scripts: build_zen4.sh, build_h100.sh"
}

# Create HPL.dat templates for different configurations
create_hpl_dat_templates() {
    log_info "Creating HPL.dat templates for different configurations..."
    
    # Zen4 HPL.dat template (optimized for 256 cores)
    cat > "${HPL_DIR}/HPL.dat.zen4" << 'EOF'
HPLinpack benchmark input file
Innovative Computing Laboratory, University of Tennessee
HPL.out      output file name (if any)
6            device out (6=stdout,7=stderr,file)
1            # of problems sizes (N)
8000         Ns
1            # of NBs
256          NBs
0            PMAP process mapping (0=Row-,1=Column-major)
1            # of process grids (P x Q)
16           Ps
16           Qs
16.0         threshold
1            # of panel fact
2            PFACTs (0=left, 1=Crout, 2=Right)
1            # of recursive stopping criterium
4            NBMINs (>= 1)
1            # of panels in recursion
2            NDIVs
1            # of recursive panel fact.
1            RFACTs (0=left, 1=Crout, 2=Right)
1            # of broadcast
1            BCASTs (0=1rg,1=1rM,2=2rg,3=2rM,4=Lng,5=LnM)
1            # of lookahead depth
1            DEPTHs (>=0)
2            SWAP (0=bin-exch,1=long,2=mix)
64           swapping threshold
0            L1 in (0=transposed,1=no-transposed) form
0            U  in (0=transposed,1=no-transposed) form
1            Equilibration (0=no,1=yes)
8            memory alignment in double (> 0)
EOF

    # H100 HPL.dat template (optimized for 64 cores)
    cat > "${HPL_DIR}/HPL.dat.h100" << 'EOF'
HPLinpack benchmark input file
Innovative Computing Laboratory, University of Tennessee
HPL.out      output file name (if any)
6            device out (6=stdout,7=stderr,file)
1            # of problems sizes (N)
4000         Ns
1            # of NBs
128          NBs
0            PMAP process mapping (0=Row-,1=Column-major)
1            # of process grids (P x Q)
8            Ps
8            Qs
16.0         threshold
1            # of panel fact
2            PFACTs (0=left, 1=Crout, 2=Right)
1            # of recursive stopping criterium
4            NBMINs (>= 1)
1            # of panels in recursion
2            NDIVs
1            # of recursive panel fact.
1            RFACTs (0=left, 1=Crout, 2=Right)
1            # of broadcast
1            BCASTs (0=1rg,1=1rM,2=2rg,3=2rM,4=Lng,5=LnM)
1            # of lookahead depth
1            DEPTHs (>=0)
2            SWAP (0=bin-exch,1=long,2=mix)
64           swapping threshold
0            L1 in (0=transposed,1=no-transposed) form
0            U  in (0=transposed,1=no-transposed) form
1            Equilibration (0=no,1=yes)
8            memory alignment in double (> 0)
EOF

    log_info "Created HPL.dat templates: HPL.dat.zen4, HPL.dat.h100"
}

# Main installation function
main() {
    log_info "Starting HPL installation for REPACSS Power-aware HPC Benchmarking"
    log_info "Target version: HPL ${HPL_VERSION}"
    
    check_dependencies
    download_hpl
    create_build_dirs
    create_makefile_templates
    create_build_scripts
    create_hpl_dat_templates
    
    log_info "HPL installation completed successfully!"
    log_info ""
    log_info "Next steps:"
    log_info "1. Build for Zen4: ./build_zen4.sh"
    log_info "2. Build for H100: ./build_h100.sh"
    log_info ""
    log_info "Directory structure:"
    log_info "  source-${HPL_VERSION}/     - HPL source code"
    log_info "  build-zen4/               - Zen4 build directory"
    log_info "  build-h100/               - H100 build directory"
    log_info "  Make.zen4                 - Zen4 Makefile template"
    log_info "  Make.h100                 - H100 Makefile template"
    log_info "  HPL.dat.zen4              - Zen4 configuration template"
    log_info "  HPL.dat.h100              - H100 configuration template"
}

# Run main function
main "$@"
