import { company, shopOpeningHours } from '../config/site';

interface PageSchemaOptions {
  homeUrl: string;
  pageUrl: string;
  title: string;
  description: string;
}

export function createSiteSchema({
  homeUrl,
  pageUrl,
  title,
  description,
}: PageSchemaOptions) {
  const businessId = new URL('#business', homeUrl).href;
  const websiteId = new URL('#website', homeUrl).href;
  const telephone = company.phoneHref.replace(/^tel:/, '');

  const business = {
    '@type': 'Electrician',
    '@id': businessId,
    name: company.name,
    url: homeUrl,
    logo: new URL('logo-elektrotechnik-hubmann.png', homeUrl).href,
    address: {
      '@type': 'PostalAddress',
      ...company.postalAddress,
    },
    telephone,
    email: company.email,
    hasMap: company.mapsHref,
    contactPoint: [
      {
        '@type': 'ContactPoint',
        contactType: 'Büro & Fachgeschäft',
        telephone,
        email: company.email,
      },
      {
        '@type': 'ContactPoint',
        contactType: 'Störungsdienst',
        telephone: company.emergencyHref.replace(/^tel:/, ''),
      },
    ],
    // The hours describe the physical shop, not emergency-service availability.
    openingHoursSpecification: shopOpeningHours.flatMap((day) =>
      [day.morning, day.afternoon].flatMap((period) =>
        period
          ? [
              {
                '@type': 'OpeningHoursSpecification',
                dayOfWeek: `https://schema.org/${day.schemaDay}`,
                opens: `${period.opens}:00`,
                closes: `${period.closes}:00`,
              },
            ]
          : [],
      ),
    ),
  };

  const website = {
    '@type': 'WebSite',
    '@id': websiteId,
    url: homeUrl,
    name: company.name,
    inLanguage: 'de-AT',
    publisher: { '@id': businessId },
  };

  const page = {
    '@type': 'WebPage',
    '@id': new URL('#webpage', pageUrl).href,
    url: pageUrl,
    name: title,
    description,
    inLanguage: 'de-AT',
    isPartOf: { '@id': websiteId },
    about: { '@id': businessId },
  };

  return {
    '@context': 'https://schema.org',
    '@graph': [business, website, page] as const,
  };
}

export function serializeStructuredData(
  schema: Record<string, unknown>,
): string {
  // JSON is embedded in HTML; a literal closing script tag must never escape it.
  return JSON.stringify(schema).replace(/</g, '\\u003c');
}
