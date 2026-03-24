/**
 * Country codes for app store scraping
 * Used across both Apple App Store and Google Play Store scrapers
 */

// Comprehensive global country list for both Apple App Store and Google Play Store
export const countries = [
  "af", // Afghanistan
  "al", // Albania
  "dz", // Algeria
  "ao", // Angola
  "ar", // Argentina
  "au", // Australia
  "at", // Austria
  "bd", // Bangladesh
  "by", // Belarus
  "be", // Belgium
  "bo", // Bolivia
  "ba", // Bosnia and Herzegovina
  "bw", // Botswana
  "br", // Brazil
  "bg", // Bulgaria
  "kh", // Cambodia
  "cm", // Cameroon
  "ca", // Canada
  "cl", // Chile
  "cn", // China
  "co", // Colombia
  "cd", // Democratic Republic of the Congo
  "cr", // Costa Rica
  "ci", // Côte d'Ivoire
  "hr", // Croatia
  "cy", // Cyprus
  "cz", // Czech Republic
  "dk", // Denmark
  "do", // Dominican Republic
  "ec", // Ecuador
  "eg", // Egypt
  "sv", // El Salvador
  "ee", // Estonia
  "fi", // Finland
  "fr", // France
  "ga", // Gabon
  "ge", // Georgia
  "de", // Germany
  "gr", // Greece
  "gt", // Guatemala
  "hn", // Honduras
  "hk", // Hong Kong
  "hu", // Hungary
  "is", // Iceland
  "in", // India
  "id", // Indonesia
  "ir", // Iran
  "iq", // Iraq
  "ie", // Ireland
  "il", // Israel
  "it", // Italy
  "jp", // Japan
  "jo", // Jordan
  "kz", // Kazakhstan
  "ke", // Kenya
  "kr", // South Korea
  "kw", // Kuwait
  "la", // Laos
  "lv", // Latvia
  "lb", // Lebanon
  "ly", // Libya
  "lt", // Lithuania
  "lu", // Luxembourg
  "mo", // Macao
  "mw", // Malawi
  "my", // Malaysia
  "mv", // Maldives
  "mx", // Mexico
  "me", // Montenegro
  "ma", // Morocco
  "mm", // Myanmar
  "nr", // Nauru
  "nl", // Netherlands
  "nz", // New Zealand
  "ni", // Nicaragua
  "ng", // Nigeria
  "no", // Norway
  "om", // Oman
  "pk", // Pakistan
  "pa", // Panama
  "py", // Paraguay
  "pe", // Peru
  "ph", // Philippines
  "pl", // Poland
  "pt", // Portugal
  "qa", // Qatar
  "ro", // Romania
  "ru", // Russia
  "rw", // Rwanda
  "sa", // Saudi Arabia
  "sn", // Senegal
  "rs", // Serbia
  "sg", // Singapore
  "sk", // Slovakia
  "si", // Slovenia
  "za", // South Africa
  "es", // Spain
  "lk", // Sri Lanka
  "se", // Sweden
  "ch", // Switzerland
  "tw", // Taiwan
  "tz", // Tanzania
  "th", // Thailand
  "xk", // Kosovo
  "to", // Tonga
  "tn", // Tunisia
  "tr", // Turkey
  "ug", // Uganda
  "ua", // Ukraine
  "ae", // United Arab Emirates
  "gb", // United Kingdom
  "us", // United States
  "uy", // Uruguay
  "vu", // Vanuatu
  "ve", // Venezuela
  "vn", // Vietnam
  "zm", // Zambia
  "zw", // Zimbabwe
];

// Aliases for backward compatibility
export const appStoreCountries = countries;
export const googlePlayCountries = countries;

// Subset of high-priority English-speaking and major market countries
export const priorityCountries = [
  "us", // United States
  "gb", // United Kingdom
  "ca", // Canada
  "au", // Australia
  "nz", // New Zealand
  "ie", // Ireland
  "za", // South Africa
];

// Major European markets
export const europeanCountries = [
  "de", // Germany
  "fr", // France
  "it", // Italy
  "es", // Spain
  "nl", // Netherlands
  "se", // Sweden
  "dk", // Denmark
  "no", // Norway
  "fi", // Finland
  "ch", // Switzerland
  "at", // Austria
  "be", // Belgium
  "pt", // Portugal
  "pl", // Poland
  "cz", // Czech Republic
  "sk", // Slovakia
  "hu", // Hungary
  "gr", // Greece
  "ro", // Romania
  "bg", // Bulgaria
  "hr", // Croatia
  "si", // Slovenia
];

// Asian markets
export const asianCountries = [
  "jp", // Japan
  "kr", // South Korea
  "cn", // China
  "in", // India
  "sg", // Singapore
  "my", // Malaysia
  "th", // Thailand
  "ph", // Philippines
  "id", // Indonesia
  "vn", // Vietnam
  "tw", // Taiwan
  "hk", // Hong Kong
];

// Latin American markets
export const latinAmericanCountries = [
  "br", // Brazil
  "mx", // Mexico
  "ar", // Argentina
  "cl", // Chile
  "co", // Colombia
  "pe", // Peru
  "ve", // Venezuela
  "ec", // Ecuador
  "uy", // Uruguay
  "py", // Paraguay
  "bo", // Bolivia
];
