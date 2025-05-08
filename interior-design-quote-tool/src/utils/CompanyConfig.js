// Configuration class for company details

export const CompanyConfig = {
  // Company information
  COMPANY_NAME: "Kart Designs & HomeProject LLP",
  COMPANY_ADDRESS: "Home Project, patancheruvu, ORR exit 3",
  COMPANY_PHONE: "+91 9009 81008",
  COMPANY_EMAIL: "info@homeproject.in",
  COMPANY_WEBSITE: "homeproject.in",
  
  // Company colors
  PRIMARY_COLOR: "#C62828",  // Dark red for accents and selected items
  HEADER_BG_COLOR: "#FFFFFF",  // White background for header
  HEADER_TEXT_COLOR: "#333333",  // Dark gray for text on white background
  
  // Helper methods
  getCompanyDetails: () => {
    return {
      name: CompanyConfig.COMPANY_NAME,
      address: CompanyConfig.COMPANY_ADDRESS,
      phone: CompanyConfig.COMPANY_PHONE,
      email: CompanyConfig.COMPANY_EMAIL,
      website: CompanyConfig.COMPANY_WEBSITE,
      contact: `${CompanyConfig.COMPANY_PHONE} | ${CompanyConfig.COMPANY_EMAIL} | ${CompanyConfig.COMPANY_WEBSITE}`
    };
  }
};