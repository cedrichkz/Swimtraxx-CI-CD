FROM ubuntu:20.04

# Update the ubuntu packages
RUN apt-get update
RUN apt-get install -y wget libx11-6 libfreetype6 libxrender1 libfontconfig1 libxext6 xvfb git

# Specify the segger version
ENV SEGGER_VERSION=622a

# Install the embedded solution tools
RUN wget https://www.segger.com/downloads/embedded-studio/Setup_EmbeddedStudio_ARM_v${SEGGER_VERSION}_linux_x64.tar.gz
RUN tar -xzvf Setup_EmbeddedStudio_ARM_v${SEGGER_VERSION}_linux_x64.tar.gz
RUN ./arm_segger_embedded_studio_v${SEGGER_VERSION}_linux_x64/install_segger_embedded_studio --copy-files-to /tools/SEGGER --accept-license

#download CMSIS support packages
RUN cd /tools/SEGGER/packages/
RUN wget https://studio.segger.com/packages/CMSIS-CORE_V5/5.7.0/CMSIS-CORE_V5.emPackage \
        https://studio.segger.com/packages/CMSIS-DSP_V5/5.7.2/CMSIS-DSP_V5.emPackage \
        https://studio.segger.com/packages/CMSIS-DOCS_V5/5.7.0/CMSIS-DOCS_V5.emPackage \
        https://studio.segger.com/packages/CMSIS-CORE.emPackage \
        https://studio.segger.com/packages/CMSIS-DSP.emPackage

#Install CMSIS support packages
RUN /tools/SEGGER/bin/pkg update
RUN /tools/SEGGER/bin/pkg install -manual CMSIS-CORE_V5.emPackage CMSIS-DSP_V5.emPackage CMSIS-DOCS_V5.emPackage CMSIS-CORE.emPackage CMSIS-DSP.emPackage
 
#Alternative method to download CMSIS packages
#RUN git clone https://capetech:LsRQZJPy732m3nvVsDFn@gitlab.com/capetech/cmis_lib_swimtraxx.git
#RUN mv cmis_lib_swimtraxx/ /tools/SEGGER/packages/

