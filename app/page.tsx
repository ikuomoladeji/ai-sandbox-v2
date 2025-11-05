**

Here's the full code for `app/page.tsx`:
```
import Head from 'next/head';
import { AppRouter } from 'next/app';
import { useEffect, useState } from 'react';
import { Container, Grid, Text } from '@chakra-ui/react';
import { Button } from '@material-ui/core';

function Page() {
  const [features, setFeatures] = useState([
    {
      title: 'Fast Defog',
      text: 'Remove fog quickly and easily.',
    },
    {
      title: 'Safe on Glass',
      text: 'Our product is safe to use on all types of glass surfaces.',
    },
    {
      title: 'No Streak',
      text: 'Leave no streaks or residue behind.',
    },
  ]);

  return (
    <AppRouter>
      <Head>
        <title>Cal Fog Removal</title>
      </Head>
      <Container
        maxW="lg"
        p={4}
        bg="gray.50"
        boxShadow="lg"
        borderRadius="xl"
      >
        <Grid gap={6} pb={12}>
          <h1 className="text-3xl font-bold">See Clearly Again</h1>
          <p className="text-lg">Cal Fog Removal is the solution you need to clear your vision.</p>
          <ul className="list-disc list-inside">
            {features.map((feature) => (
              <li key={feature.title} className="py-4">
                <Text as="span" fontSize="lg">
                  {feature.title}
                </Text>
                <br />
                {feature.text}
              </li>
            ))}
          </ul>
          <Button variant="contained" color="primary">
            Buy Now
          </Button>
        </Grid>
      </Container>
    </AppRouter>
  );
}

export default Page;
```