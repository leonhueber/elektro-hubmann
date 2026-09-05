import { describe, expect, it } from 'vitest';
import { company, formatOpeningPeriod, shopOpeningHours } from '../config/site';
import { createSiteSchema, serializeStructuredData } from './structured-data';

const title = 'Elektro Hubmann';
const description = 'Elektroinstallationen für Neubau, Sanierung und Gewerbe.';
const previewUrl = 'https://leonhueber.github.io/elektro-hubmann/';

function schemaFor(homeUrl = previewUrl, path = '') {
  return createSiteSchema({
    homeUrl,
    pageUrl: new URL(path, homeUrl).href,
    title,
    description,
  });
}

describe('structured business data', () => {
  it('uses the displayed address, contact details and supplied Maps link', () => {
    const business = schemaFor()['@graph'][0];

    expect(business['@type']).toBe('Electrician');
    expect(business.name).toBe(company.name);
    expect(business.address).toEqual({
      '@type': 'PostalAddress',
      ...company.postalAddress,
    });
    const { streetAddress, postalCode, addressLocality } = business.address;
    expect(`${streetAddress}, ${postalCode} ${addressLocality}`).toBe(
      company.address,
    );
    expect(`tel:${business.telephone}`).toBe(company.phoneHref);
    expect(business.email).toBe(company.email);
    expect(business.hasMap).toBe('https://maps.app.goo.gl/mRm8dAg8iabaR9dL7');
    expect(business.hasMap).toBe(company.mapsHref);
    expect(business.contactPoint).toEqual([
      {
        '@type': 'ContactPoint',
        contactType: 'Büro & Fachgeschäft',
        telephone: '+434286240',
        email: company.email,
      },
      {
        '@type': 'ContactPoint',
        contactType: 'Störungsdienst',
        telephone: '+436644343187',
      },
    ]);
  });

  it('keeps shop hours and structured hours in sync', () => {
    const hours = schemaFor()['@graph'][0].openingHoursSpecification;

    expect(hours).toHaveLength(8);
    for (const day of shopOpeningHours) {
      const expected = [day.morning, day.afternoon]
        .filter((period) => period !== null)
        .map(formatOpeningPeriod);
      const actual = hours
        .filter(
          (period) =>
            period.dayOfWeek === `https://schema.org/${day.schemaDay}`,
        )
        .map(
          (period) =>
            `${period.opens.slice(0, 5)}–${period.closes.slice(0, 5)}`,
        );
      expect(actual).toEqual(expected);
    }
    expect(company.shopHours).toBe(
      'Mo–Fr 09:00–12:00 und 15:00–17:30 · Mi & Fr nachmittags geschlossen',
    );
  });

  it.each(['Monday', 'Tuesday', 'Thursday'])(
    'keeps the lunch break on %s',
    (day) => {
      const business = schemaFor()['@graph'][0];
      const periods = business.openingHoursSpecification
        .filter((period) => period.dayOfWeek === `https://schema.org/${day}`)
        .map(({ opens, closes }) => [opens, closes]);
      expect(periods).toEqual([
        ['09:00:00', '12:00:00'],
        ['15:00:00', '17:30:00'],
      ]);
    },
  );

  it.each(['Wednesday', 'Friday'])(
    'does not claim afternoon opening on %s',
    (day) => {
      const periods = schemaFor()['@graph'][0].openingHoursSpecification.filter(
        (period) => period.dayOfWeek === `https://schema.org/${day}`,
      );
      expect(periods).toHaveLength(1);
      expect(periods[0]).toMatchObject({
        opens: '09:00:00',
        closes: '12:00:00',
      });
    },
  );

  it('does not invent weekend hours, ratings, prices or coordinates', () => {
    const business = schemaFor()['@graph'][0];
    expect(
      business.openingHoursSpecification.some((period) =>
        /Saturday|Sunday/.test(period.dayOfWeek),
      ),
    ).toBe(false);
    for (const property of ['aggregateRating', 'review', 'priceRange', 'geo']) {
      expect(business).not.toHaveProperty(property);
    }
  });
});

describe('linked page data', () => {
  it.each([previewUrl, 'https://elektro-hubmann.at/'])(
    'keeps URLs and entity references consistent for %s',
    (homeUrl) => {
      const home = schemaFor(homeUrl);
      const legal = schemaFor(homeUrl, 'impressum/');
      const [business, website, page] = legal['@graph'];

      expect(home['@context']).toBe('https://schema.org');
      expect(business).toEqual(home['@graph'][0]);
      expect(website).toEqual(home['@graph'][1]);
      expect(business.url).toBe(homeUrl);
      expect(business.logo).toBe(`${homeUrl}logo-elektrotechnik-hubmann.png`);
      expect(website.publisher['@id']).toBe(business['@id']);
      expect(page.isPartOf['@id']).toBe(website['@id']);
      expect(page.about['@id']).toBe(business['@id']);
      expect(page.url).toBe(`${homeUrl}impressum/`);
      expect(page['@id']).toBe(`${homeUrl}impressum/#webpage`);
      expect(page.name).toBe(title);
      expect(page.description).toBe(description);
      expect(page.inLanguage).toBe('de-AT');
      expect(new Set(legal['@graph'].map((node) => node['@id'])).size).toBe(3);
      expect(JSON.parse(serializeStructuredData(legal))).toEqual(legal);
    },
  );

  it('escapes script-closing text without changing the JSON data', () => {
    const value = {
      name: '</script><script>alert(1)</script>',
      text: 'Büro & Geschäft',
    };
    const serialized = serializeStructuredData(value);
    expect(serialized).not.toContain('<');
    expect(JSON.parse(serialized)).toEqual(value);
  });
});
